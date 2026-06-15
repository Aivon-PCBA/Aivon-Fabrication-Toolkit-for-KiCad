#!/usr/bin/env python3
"""Build a KiCad PCM-compatible plugin archive."""

import hashlib
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
GITHUB_REPO = "Aivon-PCBA/Aivon-Fabrication-Toolkit-for-KiCad"
RELEASE_ASSET_PREFIX = "AivonFabricationToolkitForKiCad"

PLUGIN_FILES = [
    "__init__.py",
    "config.py",
    "icon.png",
    "plugin.py",
    "process.py",
    "result_event.py",
    "thread.py",
    "utils.py",
]


def load_metadata():
    with open(os.path.join(ROOT, "metadata.json"), encoding="utf-8") as f:
        return json.load(f)


def release_asset_name(version):
    return f"{RELEASE_ASSET_PREFIX}_v{version}.zip"


def release_tag(version):
    return f"v{version}"


def release_download_url(version):
    asset = release_asset_name(version)
    tag = release_tag(version)
    return f"https://github.com/{GITHUB_REPO}/releases/download/{tag}/{asset}"


def write_metadata_repo_file(build_info):
    metadata = load_metadata()
    identifier = metadata["identifier"]
    version_entry = dict(metadata["versions"][0])
    version_entry.update({
        "download_size": build_info["download_size"],
        "install_size": build_info["install_size"],
        "download_sha256": build_info["download_sha256"],
        "download_url": build_info["download_url"],
    })
    repo_metadata = dict(metadata)
    repo_metadata["category"] = "fab"
    repo_metadata["versions"] = [version_entry]

    output_dir = os.path.join(ROOT, "packages", identifier)
    output_path = os.path.join(output_dir, "metadata.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(repo_metadata, output_file, indent=4, ensure_ascii=False)
        output_file.write("\n")

    print(f"  metadata_repo:  {output_path}")
    return output_path


def build_archive(output_path=None):
    metadata = load_metadata()
    version = metadata["versions"][0]["version"]

    os.makedirs(DIST, exist_ok=True)
    if output_path is None:
        output_path = os.path.join(DIST, release_asset_name(version))

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(os.path.join(ROOT, "metadata.json"), "metadata.json")
        archive.write(
            os.path.join(ROOT, "resources", "icon.png"),
            "resources/icon.png",
        )
        for name in PLUGIN_FILES:
            archive.write(
                os.path.join(ROOT, "plugins", name),
                f"plugins/{name}",
            )

    with open(output_path, "rb") as archive_file:
        download_sha256 = hashlib.sha256(archive_file.read()).hexdigest()

    download_size = os.path.getsize(output_path)
    with zipfile.ZipFile(output_path) as archive:
        install_size = sum(item.file_size for item in archive.infolist())

    print(f"Created {output_path}")
    print(f"  download_size:  {download_size}")
    print(f"  install_size:   {install_size}")
    print(f"  download_sha256: {download_sha256}")
    print(f"  download_url:   {release_download_url(version)}")

    build_info = {
        "path": output_path,
        "version": version,
        "download_size": download_size,
        "install_size": install_size,
        "download_sha256": download_sha256,
        "download_url": release_download_url(version),
    }
    write_metadata_repo_file(build_info)
    return build_info


if __name__ == "__main__":
    build_archive()
