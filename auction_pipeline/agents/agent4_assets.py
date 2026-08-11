"""
Agent 4: 미디어 & 파일 자산 관리 에이전트
- 디렉토리 구조 생성, 파일 명명 표준화, 무결성 검증, 자산 인덱스 생성
"""

import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import AssetIndex
from config import ASSETS_DIR, IMAGES_DIR, DOCS_DIR

logger = logging.getLogger("agent4")


# 표준 문서 타입 명칭
DOC_TYPES = ["현황조사서", "매각물건명세서", "건물등기", "세대열람"]

# 표준 이미지 타입 명칭
IMAGE_TYPES = [
    "map_overview",
    "map_unit_marked",
    "floor_plan",
    "hogangnono_floorplan",
    "hogangnono_unitmap",
    "price_graph_매매",
    "price_graph_전세",
]


class AssetManager:
    """자산 관리 에이전트"""

    def __init__(self, assets_dir: Path = ASSETS_DIR):
        self.assets_dir = assets_dir
        self.images_dir = assets_dir / "images"
        self.docs_dir = assets_dir / "docs"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def ensure_case_dirs(self, case_no: str) -> tuple[Path, Path]:
        safe_no = case_no.replace("-", "_")
        img_dir = self.images_dir / safe_no
        doc_dir = self.docs_dir / safe_no
        img_dir.mkdir(parents=True, exist_ok=True)
        doc_dir.mkdir(parents=True, exist_ok=True)
        return img_dir, doc_dir

    def standardize_filename(
        self, case_no: str, asset_type: str, original_path: str
    ) -> str:
        original = Path(original_path)
        suffix = original.suffix or ".png"
        safe_no = case_no.replace("-", "_")
        new_name = f"{safe_no}_{asset_type}{suffix}"
        return new_name

    def copy_and_rename(
        self,
        source_path: str,
        case_no: str,
        asset_type: str,
        target_dir: Path,
    ) -> Optional[str]:
        src = Path(source_path)
        if not src.exists():
            logger.warning(f"소스 파일 없음: {source_path}")
            return None

        new_name = self.standardize_filename(case_no, asset_type, source_path)
        dst = target_dir / new_name

        try:
            shutil.copy2(str(src), str(dst))
            logger.debug(f"  복사: {src.name} → {dst.name}")
            return str(dst)
        except Exception as e:
            logger.warning(f"  파일 복사 실패: {e}")
            return None

    def verify_file(self, file_path: str) -> bool:
        p = Path(file_path)
        if not p.exists():
            return False
        if p.stat().st_size < 100:
            logger.warning(f"  파일 크기 이상: {file_path} ({p.stat().st_size}B)")
            return False
        return True

    def compute_checksum(self, file_path: str) -> str:
        try:
            h = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def build_index(
        self,
        case_no: str,
        doc_paths: dict[str, str],
        image_paths: dict[str, str],
    ) -> AssetIndex:
        verified_docs: dict[str, str] = {}
        verified_images: dict[str, str] = {}
        all_ok = True

        for doc_type, path in doc_paths.items():
            if path and self.verify_file(path):
                verified_docs[doc_type] = path
            else:
                logger.warning(f"  문서 검증 실패: {doc_type}")
                all_ok = False

        for img_type, path in image_paths.items():
            if path and self.verify_file(path):
                verified_images[img_type] = path
            else:
                logger.warning(f"  이미지 검증 실패: {img_type}")
                all_ok = False

        return AssetIndex(
            case_no=case_no,
            docs=verified_docs,
            images=verified_images,
            verified=all_ok,
        )

    def save_index_json(self, index: AssetIndex, case_no: str) -> str:
        safe_no = case_no.replace("-", "_")
        json_path = self.assets_dir / f"{safe_no}_index.json"
        data = {
            "case_no": index.case_no,
            "generated_at": datetime.now().isoformat(),
            "verified": index.verified,
            "docs": index.docs,
            "images": index.images,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"  자산 인덱스 저장: {json_path}")
        return str(json_path)

    def load_index_json(self, case_no: str) -> Optional[dict]:
        safe_no = case_no.replace("-", "_")
        json_path = self.assets_dir / f"{safe_no}_index.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def process_case(
        self,
        case_no: str,
        agent1_docs: dict[str, str],
        agent2_images: dict[str, str],
        agent3_images: dict[str, str],
    ) -> dict:
        img_dir, doc_dir = self.ensure_case_dirs(case_no)

        # 문서 정리
        final_docs: dict[str, str] = {}
        for doc_type, src_path in agent1_docs.items():
            if src_path:
                dst = self.copy_and_rename(src_path, case_no, doc_type, doc_dir)
                if dst:
                    final_docs[doc_type] = dst

        # 이미지 정리 (agent2 + agent3 통합)
        all_images = {**agent2_images, **agent3_images}
        final_images: dict[str, str] = {}
        for img_type, src_path in all_images.items():
            if src_path:
                dst = self.copy_and_rename(src_path, case_no, img_type, img_dir)
                if dst:
                    final_images[img_type] = dst

        index = self.build_index(case_no, final_docs, final_images)
        index_path = self.save_index_json(index, case_no)

        logger.info(
            f"✓ {case_no} 자산 정리 완료 "
            f"(문서:{len(final_docs)}, 이미지:{len(final_images)}, "
            f"검증:{'OK' if index.verified else 'WARN'})"
        )

        return {
            "case_no": case_no,
            "docs": final_docs,
            "images": final_images,
            "verified": index.verified,
            "index_path": index_path,
        }

    def run(self, pipeline_data: dict) -> dict:
        result: dict = {
            "agent": "agent4_assets",
            "status": "success",
            "cases": [],
            "errors": [],
        }

        agent1_cases = {
            c["case_no"]: c for c in pipeline_data.get("agent1", {}).get("cases", [])
        }
        agent2_cases = {
            c["case_no"]: c for c in pipeline_data.get("agent2", {}).get("cases", [])
        }
        agent3_cases = {
            c["case_no"]: c for c in pipeline_data.get("agent3", {}).get("cases", [])
        }

        for case_no in agent1_cases:
            try:
                a1 = agent1_cases.get(case_no, {})
                a2 = agent2_cases.get(case_no, {})
                a3 = agent3_cases.get(case_no, {})

                # 문서 경로
                docs = (a1.get("details") or {}).get("doc_paths", {})

                # 이미지 경로
                a2_imgs: dict[str, str] = {}
                naver = a2.get("naver") or {}
                if naver.get("price_graph_path"):
                    a2_imgs["price_graph_매매"] = naver["price_graph_path"]
                if naver.get("jeonse_graph_path"):
                    a2_imgs["price_graph_전세"] = naver["jeonse_graph_path"]
                for li in naver.get("layout_info", []):
                    if li.get("floor_plan_path"):
                        a2_imgs[f"floor_plan_{li['layout_type']}"] = li["floor_plan_path"]

                a3_imgs: dict[str, str] = {}
                spatial = a3.get("spatial") or {}
                for key in ["map_overview_path", "map_unit_path",
                            "hogangnono_floor_plan_path", "hogangnono_unit_map_path"]:
                    if spatial.get(key):
                        label = key.replace("_path", "")
                        a3_imgs[label] = spatial[key]

                case_result = self.process_case(
                    case_no, docs, a2_imgs, a3_imgs
                )
                result["cases"].append(case_result)

            except Exception as e:
                result["errors"].append(f"{case_no}: {e}")
                logger.error(f"Agent4 오류 ({case_no}): {e}", exc_info=True)

        return result


def run_agent4(pipeline_data: dict) -> dict:
    manager = AssetManager()
    return manager.run(pipeline_data)


if __name__ == "__main__":
    sample = {
        "agent1": {
            "cases": [{
                "case_no": "2025-999999",
                "details": {"doc_paths": {}},
            }]
        },
        "agent2": {"cases": []},
        "agent3": {"cases": []},
    }
    result = run_agent4(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))
