# Mega-ASR: Towards In-the-Wild Speech Recognition

<p align="center">
  <b>Robust Automatic Speech Recognition for Complex Real-World Acoustic Scenarios</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue">
  <img src="https://img.shields.io/badge/PyTorch-2.x-orange">
  <img src="https://img.shields.io/badge/ASR-Robust%20Speech%20Recognition-brightgreen">
  <img src="https://img.shields.io/badge/License-Apache--2.0-green">
</p>

## Introduction

Mega-ASR is a robust automatic speech recognition project designed for in-the-wild speech recognition. It focuses on improving ASR performance under complex real-world acoustic conditions, including background noise, reverberation, far-field speech, distortion, echo, re-recording, crosstalk, and other degraded audio scenarios.

Unlike conventional ASR systems that mainly target clean or moderately noisy speech, Mega-ASR emphasizes stable recognition in medium- and high-difficulty acoustic conditions, where speech content may be partially corrupted, masked, or distorted.

This repository is currently under active development.

## Highlights

- Robust ASR for complex real-world acoustic scenarios.
- Support for dirty audio and general audio inference.
- SFT-LoRA training pipeline for acoustic robustness adaptation.
- Standard WER evaluation script.
- Modular code organization for training, inference, and evaluation.
- DAPO-LoRA training module will be released in a future version.

## Project Structure

```text
Mega-ASR/
├─ assets/
├─ configs/
├─ data/                         # ignored by git
├─ eval/
│  └─ evaluate_wer.py
└─ src_MegaASR/
   ├─ inference/
   │  ├─ inference_MegaASR_for_dirty.py
   │  └─ inference_MegaASR_for_all.py
   └─ train/
      ├─ SFT_lora/
      │  └─ SFT_lora.py
      └─ DAPO_lora/              # not released yet
```

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/Mega-ASR.git
cd Mega-ASR
pip install -r requirements.txt
```

## Inference

### Inference for Dirty Audio

```bash
python src_MegaASR/inference/inference_MegaASR_for_dirty.py \
  --audio path/to/audio.wav \
  --model_path path/to/model
```

### Inference for General Audio

```bash
python src_MegaASR/inference/inference_MegaASR_for_all.py \
  --audio path/to/audio.wav \
  --model_path path/to/model
```

## Evaluation

```bash
python eval/evaluate_wer.py \
  --pred predictions.jsonl \
  --ref references.jsonl
```

## Training

### SFT-LoRA Training

```bash
python src_MegaASR/train/SFT_lora/SFT_lora.py \
  --config configs/sft_lora.yaml
```

### DAPO-LoRA Training

The DAPO-LoRA training module is under active research and will be released in a future version.

## Roadmap

- [x] Repository structure
- [ ] Inference for dirty audio
- [ ] Inference for general audio
- [ ] WER evaluation
- [ ] SFT-LoRA training
- [ ] Model checkpoint release
- [ ] DAPO-LoRA release

## Citation

If you find this project useful, please consider citing our work. Citation information will be updated after the release of the paper.

## License

This project will be released under the Apache-2.0 License.