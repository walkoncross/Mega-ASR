import sys
sys.path.append("src")

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Mega-ASR inference")
    parser.add_argument("--audio", required=True, help="Audio path")
    parser.add_argument("--model_path", default=None)
    parser.add_argument("--lora_dir", default=None)
    parser.add_argument("--router_checkpoint", default=None)
    parser.add_argument("--quality_threshold", type=float, default=0.5)
    parser.add_argument("--language", default=None)
    parser.add_argument("--device_map", default=None)
    parser.add_argument("--no_route", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()

    from MegaASR.model.megaASR import MegaASR

    model = MegaASR(
        model_path=args.model_path,
        lora_dir=args.lora_dir,
        router_checkpoint=args.router_checkpoint,
        routing_enabled=not args.no_route,
        quality_threshold=args.quality_threshold,
        device_map=args.device_map,
    )
    result = model.infer(args.audio, language=args.language, return_route=True)
    print(result)

if __name__ == "__main__":
    main()
