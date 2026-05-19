from __future__ import annotations

import json
import os
import time
import warnings
from typing import Any

import torch
from safetensors.torch import load_file as safe_load_file


class LoRADeltaSwitch:
    def __init__(self, keep_delta_on_gpu: bool = True) -> None:
        self.keep_delta_on_gpu = keep_delta_on_gpu
        self.items: list[dict[str, Any]] = []
        self.active = False

    def _load_adapter_state(self, adapter_dir: str | os.PathLike[str]) -> dict[str, torch.Tensor]:
        adapter_dir = str(adapter_dir)
        safetensors_path = os.path.join(adapter_dir, "adapter_model.safetensors")
        bin_path = os.path.join(adapter_dir, "adapter_model.bin")

        if os.path.exists(safetensors_path):
            return safe_load_file(safetensors_path)
        return torch.load(bin_path, map_location="cpu")

    def _load_adapter_config(self, adapter_dir: str | os.PathLike[str]) -> dict[str, Any]:
        config_path = os.path.join(str(adapter_dir), "adapter_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _normalize_module_name(name: str) -> str:
        for prefix in ("base_model.model.", "model."):
            if name.startswith(prefix):
                name = name[len(prefix) :]
        
        # 兼容旧版本导出的 LoRA 路径，将 thinker.layers 映射为 thinker.model.layers
        if name.startswith("thinker.layers."):
            name = name.replace("thinker.layers.", "thinker.model.layers.", 1)
            
        return name

    def _split_lora_key(self, key: str) -> tuple[str | None, str | None]:
        key = self._normalize_module_name(key)

        for marker in (".lora_A.", ".lora_B."):
            if marker in key:
                module_name = key.split(marker)[0]
                kind = "A" if marker == ".lora_A." else "B"
                return module_name, kind

        return None, None

    def add_adapter(
        self,
        parent_module: torch.nn.Module,
        adapter_dir: str | os.PathLike[str],
        name: str,
        strip_prefixes: list[str] | None = None,
    ) -> None:
        config = self._load_adapter_config(adapter_dir)
        state = self._load_adapter_state(adapter_dir)

        lora_alpha = config.get("lora_alpha", 1)
        rank = config.get("r")
        alpha_pattern = config.get("alpha_pattern") or {}
        rank_pattern = config.get("rank_pattern") or {}
        fan_in_fan_out = bool(config.get("fan_in_fan_out", False))

        module_dict = dict(parent_module.named_modules())
        grouped: dict[str, dict[str, torch.Tensor]] = {}

        for key, tensor in state.items():
            module_name, kind = self._split_lora_key(key)
            if module_name is None or kind is None:
                continue

            if strip_prefixes:
                for prefix in strip_prefixes:
                    if module_name.startswith(prefix):
                        module_name = module_name[len(prefix) :]

            grouped.setdefault(module_name, {})[kind] = tensor.cpu()

        loaded = 0
        missing = []

        for module_name, pair in grouped.items():
            if "A" not in pair or "B" not in pair:
                continue
            if module_name not in module_dict:
                missing.append(module_name)
                continue

            module = module_dict[module_name]
            if not hasattr(module, "weight"):
                missing.append(module_name)
                continue

            a_matrix = pair["A"].float()
            b_matrix = pair["B"].float()
            adapter_rank = rank_pattern.get(module_name, rank)
            if adapter_rank is None:
                adapter_rank = a_matrix.shape[0]
            adapter_alpha = alpha_pattern.get(module_name, lora_alpha)
            scaling = float(adapter_alpha) / float(adapter_rank)

            delta = torch.matmul(b_matrix, a_matrix) * scaling
            weight = module.weight

            if fan_in_fan_out:
                delta = delta.T

            if delta.shape != weight.shape:
                try:
                    delta = delta.reshape(weight.shape)
                except Exception:
                    missing.append(
                        f"{module_name}: delta shape {tuple(delta.shape)} != "
                        f"weight shape {tuple(weight.shape)}"
                    )
                    continue

            delta = delta.to(dtype=weight.dtype)
            if self.keep_delta_on_gpu:
                delta = delta.to(device=weight.device)

            self.items.append(
                {
                    "name": name,
                    "module_name": module_name,
                    "weight": weight,
                    "delta": delta,
                }
            )
            loaded += 1

        if missing:
            warnings.warn(
                f"LoRA adapter {name} loaded {loaded} deltas, "
                f"missing {len(missing)} modules. Examples: {missing[:5]}",
                stacklevel=2,
            )

    @torch.no_grad()
    def set_active(self, active: bool) -> float:
        if self.active == active:
            return 0.0

        start = time.perf_counter()
        sign = 1.0 if active else -1.0

        for item in self.items:
            weight = item["weight"]
            delta = item["delta"]
            if delta.device != weight.device:
                delta = delta.to(device=weight.device)
            weight.data.add_(delta, alpha=sign)

        self.active = active
        return time.perf_counter() - start
