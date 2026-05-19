<p align="center">
  <img src="assets/figures/mega_asr_logo.png" alt="Mega-ASR Logo" width="100">
</p>
<h1 align="center">Mega-ASR: Towards In-the-Wild^2 Speech Recognition via Scaling Up Real-world Acoustic Simulation</h1>
<p align="center">
  <b>You’ll come back to Mega-ASR — after finding the rest fail in the real world.
  </b> 
</p>

<p align="center">
  <a href="https://xzf-thu.github.io/Mega-ASR/">
    <img src="https://img.shields.io/badge/Project-Homepage-purple">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10+-blue">
  <img src="https://img.shields.io/badge/PyTorch-2.x-orange">
  <img src="https://img.shields.io/badge/ASR-Robust%20Speech%20Recognition-brightgreen">
  <img src="https://img.shields.io/badge/License-Apache--2.0-green">
</p>

<p align="center">
  <img src="/docs/assets/dataset.png" alt="Mega-ASR Logo" width="100%">
</p>





| Audio | Ground Truth | Mega-ASR (Ours) | Qwen3-ASR | Gemini-3-Pro | Seed-ASR | Whisper |
|---|---|---|---|---|---|---|
| <video src="assets/case_study/empty_output_recovery.mp4" controls width="240"></video> | ...and said to him let us go and eat some honey. Whose honey? inquired Kobay cautiously. My father's, Soongoora replied. Oh, all right, I'm with you, said the tortoise eagerly, and away they went.<br><br>*Reference* | <span style="color:#ef4444">He</span> said to him <span style="color:#ef4444">let's</span> go and eat some honey. <span style="color:#ef4444">It's</span> honey? inquired <span style="color:#ef4444">very</span> cautiously. My father <span style="color:#ef4444">is Superabundant</span> — oh, all right, <span style="color:#ef4444">I will</span>, said <span style="color:#ef4444">to her</span> eagerly, and away they went.<br><br>**WER: <span style="color:#22c55e">47.1</span> ✅** | <span style="color:#ef4444">&lt;empty&gt;</span><br><br>**WER: <span style="color:#ef4444">100.0</span> 🔴** | <span style="color:#ef4444">But tell me, that's how she met</span> my father<span style="color:#ef4444">'s sister</span>. Oh, all right. <span style="color:#ef4444">I wish... I really...</span><br><br>**WER: <span style="color:#ef4444">86.1</span> 🔴** | My father <span style="color:#ef4444">is</span>. Oh, all right, <span style="color:#ef4444">I wish you can</span>.<br><br>**WER: <span style="color:#ef4444">85.3</span> 🔴** | ...to him... some honey... <span style="color:#ef4444">oh yeah</span>...<br><br>**WER: <span style="color:#ef4444">92.5</span> 🔴** |
| <video src="assets/case_study/long_utterance_recovery.mp4" controls width="240"></video> | To waste, I skip forty years, said the baker in tears, and proceed without further remark to the day when you took me aboard your ship to help you in hunting the snark.<br><br>*Reference* | <span style="color:#ef4444">To witness,</span> I skip forty years, said the baker in tears, and proceed without further remark to the day when you took me aboard <span style="color:#ef4444">of</span> your ship to help you in hunting the snark.<br><br>**WER: <span style="color:#22c55e">5.9</span> ✅** | <span style="color:#ef4444">I skipped 40 years. Second day in here. Ever since you left, I've been a monk...</span><br><br>**WER: <span style="color:#ef4444">64.7</span> 🟠** | <span style="color:#ef4444">I spent forty years at sea and never seen a rougher than</span> the day <span style="color:#ef4444">that</span> you took me aboard your ship...<br><br>**WER: <span style="color:#ef4444">64.7</span> 🟠** | <span style="color:#ef4444">To wait.</span> I skip forty years. <span style="color:#ef4444">Saturday and years.</span> And proceed without further remark...<br><br>**WER: <span style="color:#ef4444">38.2</span> 🟡** | I skip forty years... to the day you took me <span style="color:#ef4444">on a ship</span>... to hunt the <span style="color:#ef4444">shark</span>.<br><br>**WER: <span style="color:#ef4444">71.5</span> 🟠** |

<details>
<summary>More examples</summary>

| Audio | Ground Truth | Mega-ASR (Ours) | Qwen3-ASR | Gemini-3-Pro | Seed-ASR | Whisper |
|---|---|---|---|---|---|---|
| <video src="assets/case_study/babble_noise_hallucination.mp4" controls width="240"></video> | The friendly gang left the drug store.<br><br>*Reference* | <span style="color:#22c55e">The friendly gang left the drug store.</span><br><br>**WER: <span style="color:#22c55e">8.0</span> ✅** | <span style="color:#ef4444">It's a</span> friendly gang. <span style="color:#ef4444">That's the drug gang.</span><br><br>**WER: <span style="color:#ef4444">57.1</span> 🟠** | <span style="color:#ef4444">Friendly</span> gang left the <span style="color:#ef4444">drugs</span>.<br><br>**WER: <span style="color:#ef4444">42.9</span> 🟡** | The friendly gang left the <span style="color:#ef4444">drugstore</span>.<br><br>**WER: <span style="color:#22c55e">28.6</span> 🟢** | <span style="color:#ef4444">A</span> friendly <span style="color:#ef4444">young man</span> left the drug store.<br><br>**WER: <span style="color:#ef4444">62.3</span> 🟠** |
| <video src="assets/case_study/restaurant_noise_recovery.mp4" controls width="240"></video> | The set of china hit the floor with a crash.<br><br>*Reference* | <span style="color:#22c55e">The set of china hit the floor with a crash.</span><br><br>**WER: <span style="color:#22c55e">8.0</span> ✅** | The <span style="color:#ef4444">bed is fine. It</span> hit the floor with a crash.<br><br>**WER: <span style="color:#ef4444">40.0</span> 🟡** | <span style="color:#ef4444">He said it's fine I</span> hit the <span style="color:#ef4444">forward slash</span>.<br><br>**WER: <span style="color:#ef4444">100.0</span> 🔴** | The <span style="color:#ef4444">sound</span> of china <span style="color:#ef4444">hits</span> the floor with a crash.<br><br>**WER: <span style="color:#22c55e">20.0</span> 🟢** | The <span style="color:#ef4444">chef</span> of <span style="color:#ef4444">China</span> hit the floor with a <span style="color:#ef4444">clash</span>.<br><br>**WER: <span style="color:#ef4444">55.0</span> 🟠** |
| <video src="assets/case_study/financial_entity_recovery.mp4" controls width="240"></video> | Among export-led electrical and computer makers, Japan Victor Company fell fifty to two thousand three hundred twenty.<br><br>*Reference* | Among export-led <span style="color:#ef4444">(missing: electrical and)</span> computer makers, Japan Victor Company fell fifty to two thousand three hundred twenty.<br><br>**WER: <span style="color:#22c55e">11.1</span> ✅** | Among export-led <span style="color:#ef4444">(missing: electrical and)</span> computer makers, Japan <span style="color:#ef4444">VictorNet sold fifty-two thousand three hundred fifty</span>.<br><br>**WER: <span style="color:#ef4444">38.9</span> 🟡** | Among export-led <span style="color:#ef4444">(missing: electrical and)</span> computer makers, Japan Victor <span style="color:#ef4444">Co.</span> fell <span style="color:#ef4444">50</span> to <span style="color:#ef4444">2,350 yen</span>.<br><br>**WER: <span style="color:#ef4444">35.7</span> 🟡** | Among export-led <span style="color:#ef4444">in</span> computer makers, Japan Victor Company <span style="color:#ef4444">sell 50 to 2300 unit</span>.<br><br>**WER: <span style="color:#ef4444">50.0</span> 🟠** | Among <span style="color:#ef4444">exporters,</span> computer makers <span style="color:#ef4444">in Japan victor companies sold</span> fifty...<br><br>**WER: <span style="color:#ef4444">66.7</span> 🟠** |
| <video src="assets/case_study/phrase_recovery.mp4" controls width="240"></video> | Has exposure really been reduced?<br><br>*Reference* | <span style="color:#22c55e">Has exposure really been reduced</span><span style="color:#ef4444">.</span><br><br>**WER: <span style="color:#22c55e">8.0</span> ✅** | Has exposure really <span style="color:#ef4444">done you?</span><br><br>**WER: <span style="color:#ef4444">40.0</span> 🟡** | Has <span style="color:#ef4444">the closure</span> really <span style="color:#ef4444">affected you?</span><br><br>**WER: <span style="color:#ef4444">80.0</span> 🔴** | Has exposure <span style="color:#ef4444">to beauty products.</span><br><br>**WER: <span style="color:#ef4444">60.0</span> 🟠** | <span style="color:#ef4444">Have those who</span> really <span style="color:#ef4444">been refused?</span><br><br>**WER: <span style="color:#ef4444">78.5</span> 🔴** |

</details>



## 🔥🔥🔥 News!!

- **May 20, 2025**: 🔥 We release **Mega-ASR**. Model weights on Hugging Face are coming soon.
- **May 20, 2025**: 🔥 We release **Voices-in-the-Wild-2M**, a benchmark for in-the-wild ASR robustness evaluation. [[Dataset]](https://huggingface.co/datasets/zhifeixie/Voices-in-the-Wild-test-v2)
- **Coming soon**: 🔥 We will release the **DAPO-LoRA training code**.


**Overview**

* **[Introduction](#introduction)**
* **[Model Download](#model-download)**
* **[Quick Start](#quick-start)**
* **[Inference](#inference)**
* **[Evaluation](#evaluation)**
* **[Dirty Speech Data Generation](#dirty-speech-data-generation)**
* **[Finetune](#finetune)**
* **[Citation](#citation)**
* **[License](#license)**


## Introduction

Mega-ASR is designed for speech recognition in complex real-world acoustic environments, where speech signals are often affected by noise, reverberation, far-field recording, low volume, distortion, stuttering, echo, obstruction, and multiple overlapping interferences. Unlike general-purpose ASR systems that mainly perform well on clean or moderately noisy speech, Mega-ASR focuses on medium- and high-error-rate audio conditions, where recognition stability becomes more challenging.

- **Robust dirty and general ASR**: supports stable recognition for both in-the-wild dirty speech and general audio.
- **2M-scale dirty speech corpus**: covers noise, far-field recording, distortion, stuttering, echo, obstruction, and mixed acoustic interference.
- **SFT + RL robustness training**: improves recognition stability under complex acoustic conditions through supervised fine-tuning and reinforcement learning.


## Model Download

| Model | Description | Download |
|---|---|---|
| **Mega-ASR for Dirty** | Optimized for dirty speech scenarios. | Coming soon |
| **Mega-ASR for All** | Adds a routing module that automatically selects the recognition path for clean or degraded speech. | Coming soon |


## Quick Start

```bash
conda create -n mega-asr2 python=3.12 -y
conda activate mega-asr2

pip install torch==2.10.0 torchaudio==2.10.0 torchvision==0.25.0
pip install -r mega_asr_requirements.txt
pip install -e /path/to/Qwen3-ASR --no-deps
```


## Inference

For dirty / degraded audio:

```bash
bash scripts/inference_MegaASR_for_dirty.sh
```

For general audio with automatic routing:

```bash
bash scripts/web_inference_MegaASR_for_all.sh
```


## Evaluation

Run Qwen3-ASR inference and compute WER (English) / CER (Chinese) on JSONL data:

```bash
CUDA_VISIBLE_DEVICES=6,7 python evaluate_wer.py \
  --input_jsonl example/examples.jsonl \
  --output_jsonl output_with_wer.jsonl
```

Each input line requires `audio_path` and `answer` (ground-truth transcription). Place `evaluate_wer.py` and `cn_tn.py` (used for Chinese text normalization) in the same directory.


## Dirty Speech Data Generation

The data generation code for our Voices-in-the-Wild training data is provided under `dataset/dataloader/`, with `scheduler.py` as the core scheduling entry.

Detailed implementations of individual perturbation functions and exact parameter settings for acoustic corruptions are not included in this public release.


## Finetune

Mega-ASR supports robustness adaptation through supervised fine-tuning (A2S-SFT) and reinforcement learning (DG-WGPO).

```bash
bash A2S-SFT_stage1.sh
bash A2S-SFT_stage2.sh
bash A2S-SFT_stage3.sh
```

Training data is in JSONL format:

```json
{
  "audio": ".../wavs/test-clean/61/70968/61-70968-0000.wav",
  "text": "language English<asr_text>THE TRANSCRIPT TEXT",
  "prompt": ""
}
```

The DG-WGPO reinforcement learning module will be released in a future update.


## Citation

Citation information will be updated after the release of the paper.


## License

This project will be released under the Apache-2.0 License.

