import json
import os
from langchain.docstore.document import Document


def detect_changes(new_data, prev_data):
    new_dict = {item["서비스ID"]: item for item in new_data}
    prev_dict = {item["서비스ID"]: item for item in prev_data}

    added, updated, deleted = [], [], []

    for sid, item in new_dict.items():
        if sid not in prev_dict:
            added.append(item)
        elif json.dumps(item, sort_keys=True, ensure_ascii=False) != json.dumps(prev_dict[sid], sort_keys=True, ensure_ascii=False):
            updated.append(item)

    for sid in prev_dict:
        if sid not in new_dict:
            deleted.append(prev_dict[sid])

    return added, updated, deleted

def convert_to_documents(items):
    documents = []
    for item in items:
        조건_태그 = [k for k, v in item.get("조건", {}).items() if v]

        content = f"""
서비스명: {item.get('서비스명')}
서비스목적: {item.get('서비스목적')}
지원대상: {item.get('지원대상')}
지원내용: {item.get('지원내용')}
신청방법: {item.get('신청방법')}
신청기한: {item.get('신청기한')}
선정기준: {item.get('선정기준')}
구비서류: {item.get('구비서류')}
소관기관: {item.get('소관기관명')}
문의처: {item.get('문의처')}
온라인신청URL: {item.get('온라인신청사이트URL')}
법령: {item.get('법령')}
해당 조건: {', '.join(조건_태그)}
        """

        doc = Document(
            page_content=content.strip(),
            metadata={
                "서비스ID": item.get("서비스ID"),
                "서비스명": item.get("서비스명"),
                "조건": item.get("조건", {}),
                "원본": item
            }
        )
        documents.append(doc)

    return documents