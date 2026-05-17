<p align="center">
  <img src="assets/figures/mega_asr_logo.png" alt="Mega-ASR Logo" width="220">
</p>

<h1 align="center">Mega-ASR: Towards In-the-Wild Speech Recognition</h1>

<p align="center">
  <b>Robust Automatic Speech Recognition for Complex Real-World Acoustic Scenarios</b>
</p>

<p align="center">
  <a href="https://xzf-thu.github.io/Mega-ASR/"><b>Homepage</b></a> |
  <a href="#model-download"><b>Model Download</b></a> |
  <a href="#installation"><b>Our Bench Download</b></a> |
  <a href="#paper"><b>Paper</b></a> |
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



<p>
We present <b>Mega-ASR</b>, an open-source speech recognition model designed for stable and robust ASR under complex dirty speech conditions, especially on medium- and high-error-rate audio.

<p>
This repository contains the official implementation, model weights, core training data, and evaluation toolkit for Mega-ASR.
</p>


<p align="center">
  <b>🚀 When conventional ASR systems fail under real-world acoustic interference, come to Mega-ASR!</b>
</p>




## Case Study

The following examples show how Mega-ASR recovers speech content under challenging dirty speech conditions. Click **Listen** to play each audio sample.

| Audio & Challenge | Ground Truth | **Mega-ASR (Ours)** | Qwen3-ASR | Gemini-3-Pro | Seed-ASR | Whisper |
|---|---|---|---|---|---|---|
| [▶️ Listen](assets/case_study/empty_output_recovery.wav)<br><b>Empty Output Recovery</b> | "...and said to him let us go and eat some honey. Whose honey? inquired Kobay cautiously. My father's, Soongoora replied. Oh, all right, I'm with you, said the tortoise eagerly, and away they went." | ✅ **WER 47.1**<br>"He said to him let's go and eat some honey. It's honey? he inquired very cautiously. My father is Superabundant — oh, all right, I will, he said to her eagerly, and away they went." | 🔴 **WER 100.0**<br><i>&lt;empty&gt;</i> | 🔴 **WER 86.1**<br>"But tell me, that's how she met my father's sister. Oh, alright. I wish... I really..." | 🔴 **WER 85.3**<br>"My father is. Oh, all right, I wish you can." | 🔴 **WER 92.5**<br>"...to him... some honey... oh yeah..." |
| [▶️ Listen](assets/case_study/long_utterance_recovery.wav)<br><b>Long-Utterance Semantic Recovery</b> | "To waste, I skip forty years, said the baker in tears, and proceed without further remark to the day when you took me aboard your ship to help you in hunting the snark." | ✅ **WER 5.9**<br>"To witness, I skip forty years, said the baker in tears, and proceed without further remark to the day when you took me aboard of your ship to help you in hunting the snark." | 🟠 **WER 64.7**<br>"I skipped 40 years. Second day in here. Ever since you left, I've been a monk..." | 🟠 **WER 64.7**<br>"I spent forty years at sea and never seen a rougher than the day that you took me aboard your ship..." | 🟡 **WER 38.2**<br>"To wait. I skip forty years. Saturday and years. And proceed without further remark..." | 🟠 **WER 71.5**<br>"I skip forty years... to the day you took me on a ship... to hunt the shark." |
| [▶️ Listen](assets/case_study/babble_noise_hallucination.wav)<br><b>Babble Noise & Hallucination</b> | "The friendly gang left the drug store." | ✅ **WER 8.0**<br>"The friendly gang left the drug store." | 🟠 **WER 57.1**<br>"It's a friendly gang. That's the drug gang." | 🟡 **WER 42.9**<br>"Friendly gang left the drugs." | 🟢 **WER 28.6**<br>"The friendly gang left the drugstore." | 🟠 **WER 62.3**<br>"A friendly young man left the drug store." |
| [▶️ Listen](assets/case_study/restaurant_noise_recovery.wav)<br><b>Restaurant Noise Recovery</b> | "The set of china hit the floor with a crash." | ✅ **WER 8.0**<br>"The set of china hit the floor with a crash." | 🟡 **WER 40.0**<br>"The bed is fine. It hit the floor with a crash." | 🔴 **WER 100.0**<br>"He said it's fine I hit the forward slash." | 🟢 **WER 20.0**<br>"The sound of china hits the floor with a crash." | 🟠 **WER 55.0**<br>"The chef of China hit the floor with a clash." |
| [▶️ Listen](assets/case_study/financial_entity_recovery.wav)<br><b>Financial Entity Recovery</b> | "Among export-led electrical and computer makers, Japan Victor Company fell fifty to two thousand three hundred twenty." | ✅ **WER 11.1**<br>"Among export-led computer makers, Japan Victor Company fell fifty to two thousand three hundred twenty." | 🟡 **WER 38.9**<br>"Among export-led computer makers, Japan VictorNet sold fifty-two thousand three hundred fifty." | 🟡 **WER 35.7**<br>"Among export-led computer makers, Japan Victor Co. fell 50 to 2,350 yen." | 🟠 **WER 50.0**<br>"Among export-led in computer makers, Japan Victor Company sell 50 to 2300 unit." | 🟠 **WER 66.7**<br>"Among exporters, computer makers in Japan victor companies sold fifty..." |
| [▶️ Listen](assets/case_study/phrase_recovery.wav)<br><b>Phrase Recovery</b> | "Has exposure really been reduced?" | ✅ **WER 8.0**<br>"Has exposure really been reduced." | 🟡 **WER 40.0**<br>"Has exposure really done you?" | 🔴 **WER 80.0**<br>"Has the closure really affected you?" | 🟠 **WER 60.0**<br>"Has exposure to beauty products." | 🔴 **WER 78.5**<br>"Have those who really been refused?" |



## 🔥🔥🔥 News!!

- **May 20, 2025**: 🔥 We release **Mega-ASR**. Model weights on Hugging Face are coming soon.
- **May 20, 2025**: 🔥 We release **Voices-in-the-Wild-2M**, a benchmark for in-the-wild ASR robustness evaluation. [[Dataset]](https://huggingface.co/datasets/zhifeixie/Voices-in-the-Wild-test-v2)
- **Coming soon**: 🔥 We will release the **DAPO-LoRA training code**.

## Contents

- [Introduction](#introduction)
- [Model Download](#model-download)
- [Main Results](#main-results)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Inference](#inference)
- [Finetune](#finetune)
- [Evaluation](#evaluation)



## Introduction


Mega-ASR is designed for speech recognition in complex real-world acoustic environments, where speech signals are often affected by noise, reverberation, far-field recording, low volume, distortion, stuttering, echo, obstruction, and multiple overlapping interferences. Unlike general-purpose ASR systems that mainly perform well on clean or moderately noisy speech, Mega-ASR focuses on medium- and high-error-rate audio conditions, where recognition stability becomes more challenging.

To improve robustness, Mega-ASR is built with large-scale dirty speech data and a two-stage robustness training pipeline. The released resources include model weights, core training data, evaluation benchmarks, and WER/CER evaluation scripts, enabling reproducible research and further development of robust ASR systems for in-the-wild scenarios.

- **Robust dirty and general ASR**: supports stable recognition for both in-the-wild dirty speech and general audio.
- **2M-scale dirty speech corpus**: covers noise, far-field recording, distortion, stuttering, echo, obstruction, and mixed acoustic interference.
- **SFT + RL robustness training**: improves recognition stability under complex acoustic conditions through supervised fine-tuning and reinforcement learning.
- **Reproducible WER/CER evaluation**: provides standard scripts and benchmarks for ASR robustness evaluation.
- **DAPO-LoRA roadmap**: reinforcement learning training code will be released in a future update.


## Model Download

We provide two Mega-ASR model variants for different usage scenarios.

| Model | Description | Download |
|---|---|---|
| **Mega-ASR for Dirty** | Optimized for dirty speech scenarios, including noisy, far-field, low-volume, degraded, and hard-to-recognize audio. | Coming soon |
| **Mega-ASR for All** | Built upon Mega-ASR for Dirty with a lightweight routing module that automatically distinguishes clean speech from degraded speech and selects the appropriate recognition path. | Coming soon |

After downloading the model weights, please specify the model path in the corresponding inference script or pass it through command-line arguments.


## Project Structure


<p align="center">
  <img src="assets/figures/method_overview.png" alt="Mega-ASR Method Overview" width="95%">
</p>

<p align="center">
  <b>Figure 1.</b> Overview of the Mega-ASR training pipeline, including acoustic-to-speech supervised fine-tuning and reward-based optimization for robust speech recognition.
</p>

```text
Mega-ASR/
├─ assets/
│  └─ Figures, logos, and other README resources.
│
├─ configs/
│  └─ Configuration files for SFT-LoRA and DAPO-LoRA training.
│
├─ data/
│  └─ Local data directory. Large-scale audio data is not tracked by Git.
│
├─ eval/
│  └─ evaluate_wer.py
│     WER/CER evaluation utilities for ASR robustness testing.
│
└─ src_MegaASR/
   ├─ inference/
   │  ├─ inference_MegaASR_for_dirty.py
   │  │  Dirty-speech inference without routing, designed for degraded audio.
   │  │
   │  └─ inference_MegaASR_for_all.py
   │     General inference with routing, supporting both dirty and general audio.
   │
   └─ train/
      ├─ SFT_lora/
      │  └─ SFT_lora.py
      │     SFT-LoRA training pipeline for acoustic robustness adaptation.
      │
      └─ DAPO_lora/
         └─ DAPO-LoRA training module, to be released in a future update.
```

## Main Results

Mega-ASR is evaluated across three benchmark families, including noisy and robust ASR benchmarks, Voices-in-the-Wild-Bench, and standard ASR benchmarks. Lower WER/CER indicates better recognition performance.

<p align="center">
  <img src="assets/figures/radar_results.png" alt="Radar comparison of Mega-ASR" width="95%">
</p>

<p align="center">
  <b>Figure 2.</b> Radar comparison of Qwen3-ASR-1.7B and Mega-ASR across selected ASR evaluation subsets.
</p>

### Noisy and Robust ASR Benchmarks

<p align="center">
  <img src="assets/tables/noisy_robust_asr_benchmarks.png" alt="Performance comparison on noisy and robust ASR benchmarks" width="95%">
</p>

<p align="center">
  <b>Table 1.</b> Performance comparison on noisy and robust ASR benchmarks.
</p>

### Voices-in-the-Wild-Bench

<p align="center">
  <img src="assets/tables/voices_in_the_wild_breakdown.png" alt="Breakdown results on Voices-in-the-Wild-Bench" width="95%">
</p>

<p align="center">
  <b>Table 2.</b> Breakdown results on Voices-in-the-Wild-Bench by acoustic scenario.
</p>

### Standard ASR Benchmarks

<p align="center">
  <img src="assets/tables/standard_asr_benchmarks.png" alt="Performance comparison on standard ASR benchmarks" width="95%">
</p>

<p align="center">
  <b>Table 3.</b> Performance comparison on standard ASR benchmarks. For LibriSpeech, each entry is reported as clean/other.
</p>

## Quick Start

### 1. Create Environment

We recommend using Conda to create an isolated Python environment.

```bash
conda create -n mega-asr2 python=3.12 -y
conda activate mega-asr2
```

Upgrade basic Python build tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 2. Install PyTorch

Install PyTorch with CUDA 12.8 support:

```bash
pip install \
  torch==2.9.1+cu128 \
  torchaudio==2.9.1+cu128 \
  torchvision==0.24.1+cu128 \
  --index-url https://download.pytorch.org/whl/cu128
```

### 3. Install Mega-ASR Dependencies

```bash
pip install -r mega_asr_requirements.txt
```

### 4. Install Qwen3-ASR Dependency

Mega-ASR is built upon Qwen3-ASR. Please prepare the Qwen3-ASR source code locally and install it in editable mode:

```bash
pip install -e /path/to/Qwen3-ASR --no-deps
```

For example, replace `/path/to/Qwen3-ASR` with the actual local path of your Qwen3-ASR repository.

## Inference

Mega-ASR provides two inference modes for different usage scenarios.



### 1. Inference for Dirty Audio

This mode is designed for degraded or hard-to-recognize speech, such as noisy, far-field, distorted, or mixed-interference audio.



```bash
python src_MegaASR/inference/inference_MegaASR_for_dirty.py \
  --audio path/to/audio.wav \
  --model_path path/to/model
```

### 2. Inference for General Audio

This mode supports both dirty speech and general audio. It uses a routing mechanism to select the appropriate recognition path automatically.



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



## Finetune

Mega-ASR supports acoustic robustness adaptation through both supervised fine-tuning and reinforcement learning based optimization.



### 1. SFT-LoRA Training

SFT-LoRA is used to adapt Mega-ASR to complex dirty speech scenarios with supervised training data.


```bash
python src_MegaASR/train/SFT_lora/SFT_lora.py \
  --config configs/sft_lora.yaml
```

### 2. DAPO-LoRA Training

DAPO-LoRA is designed for reinforcement learning based robustness optimization after supervised fine-tuning.


The DAPO-LoRA training module is under active research and will be released in a future update.

## Evaluation

We provide standard WER/CER evaluation utilities for ASR robustness testing.

```bash
python eval/evaluate_wer.py \
  --pred predictions.jsonl \
  --ref references.jsonl
```


## Citation

If you find this project useful, please consider citing our work. Citation information will be updated after the release of the paper.

## License

This project will be released under the Apache-2.0 License.