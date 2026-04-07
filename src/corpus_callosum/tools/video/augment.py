"""Transcript augmentation and manual editing support."""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

from .config import VideoConfig


class TranscriptAugmenter:
    """Handle manual transcript augmentation and finalization."""

    def __init__(self, config: VideoConfig):
        """Initialize transcript augmenter.

        Args:
            config: Video configuration
        """
        self.config = config

    def open_in_editor(self, file_path: Path) -> None:
        """Open a file in the system default editor.

        Args:
            file_path: Path to file to open
        """
        file_path = Path(file_path)
        system = platform.system()
        
        if system == "Windows":
            os.startfile(str(file_path))
        elif system == "Darwin":
            subprocess.run(["open", str(file_path)])
        else:
            editor = os.environ.get("EDITOR", "xdg-open")
            subprocess.run([editor, str(file_path)])

    def augment(
        self,
        transcript_path: Path,
        output_path: Optional[Path] = None,
        auto_save: bool = False,
    ) -> Path:
        """Augment a transcript with manual edits.

        Args:
            transcript_path: Path to cleaned transcript
            output_path: Optional final output path
            auto_save: If True, skip editor and just copy to output

        Returns:
            Path to final augmented transcript
        """
        transcript_path = Path(transcript_path)
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

        if not auto_save:
            # Open in editor for manual annotation
            print("\n── Manual Annotation ──")
            print("The transcript will open in your editor.")
            print("Add your annotations, then save and close.")
            print("Press Enter to continue...")
            input()
            
            self.open_in_editor(transcript_path)
            
            print("\nPress Enter when you have finished editing...")
            input()

        # Read the (possibly edited) content
        final_content = transcript_path.read_text(encoding="utf-8")

        # Determine output path
        if output_path is None:
            output_path = transcript_path.parent / f"{transcript_path.stem}_final{transcript_path.suffix}"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check for overwrite
        if output_path.exists() and not auto_save:
            response = input(f"\n{output_path.name} already exists. Overwrite? [y/N]: ")
            if response.lower() not in ["y", "yes"]:
                # Save to scratch instead
                fallback = transcript_path.parent / f"{transcript_path.stem}_fallback{transcript_path.suffix}"
                fallback.write_text(final_content, encoding="utf-8")
                print(f"Saved to: {fallback}")
                return fallback

        # Write final transcript
        output_path.write_text(final_content, encoding="utf-8")
        print(f"\n✓ Final transcript written to: {output_path}")
        
        return output_path
