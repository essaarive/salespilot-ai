import re

TARGET_CHUNK_LENGTH = 560
MAX_CHUNK_LENGTH = 700
MIN_CHUNK_LENGTH = 80
OVERLAP_LENGTH = 60


def clean_text(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str) -> list[str]:
    cleaned = clean_text(text)
    if not cleaned:
        return []

    paragraphs = split_paragraphs(cleaned)
    chunks: list[str] = []
    buffer = ""

    for paragraph in paragraphs:
        parts = split_long_text(paragraph)
        for part in parts:
            if not part:
                continue

            if len(part) > MAX_CHUNK_LENGTH:
                for hard_part in hard_split(part):
                    chunks = append_chunk(chunks, hard_part)
                continue

            if not buffer:
                buffer = part
                continue

            if len(buffer) + len(part) + 2 <= TARGET_CHUNK_LENGTH:
                buffer = f"{buffer}\n\n{part}"
            else:
                chunks = append_chunk(chunks, buffer)
                buffer = with_overlap(buffer, part)

    if buffer:
        chunks = append_chunk(chunks, buffer)

    return [chunk for chunk in chunks if should_keep_chunk(chunk)]


def split_paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", text)
    paragraphs: list[str] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if len(block) <= TARGET_CHUNK_LENGTH:
            paragraphs.append(block)
        else:
            paragraphs.extend(split_by_line(block))
    return paragraphs


def split_by_line(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    parts: list[str] = []
    buffer = ""
    for line in lines:
        if not buffer:
            buffer = line
        elif len(buffer) + len(line) + 1 <= TARGET_CHUNK_LENGTH:
            buffer = f"{buffer}\n{line}"
        else:
            parts.append(buffer)
            buffer = line
    if buffer:
        parts.append(buffer)
    return parts


def split_long_text(text: str) -> list[str]:
    if len(text) <= MAX_CHUNK_LENGTH:
        return [text]

    sentences = re.split(r"(?<=[。！？!?；;])", text)
    parts: list[str] = []
    buffer = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if not buffer:
            buffer = sentence
        elif len(buffer) + len(sentence) <= TARGET_CHUNK_LENGTH:
            buffer += sentence
        else:
            parts.append(buffer)
            buffer = sentence

    if buffer:
        parts.append(buffer)
    return parts or hard_split(text)


def hard_split(text: str) -> list[str]:
    parts: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + MAX_CHUNK_LENGTH, len(text))
        parts.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - OVERLAP_LENGTH, start + 1)
    return parts


def with_overlap(previous: str, current: str) -> str:
    previous = previous.strip()
    if len(previous) <= OVERLAP_LENGTH:
        return current
    return f"{previous[-OVERLAP_LENGTH:]}\n\n{current}"


def append_chunk(chunks: list[str], chunk: str) -> list[str]:
    chunk = clean_text(chunk)
    if not should_keep_chunk(chunk):
        return chunks
    if len(chunk) <= MAX_CHUNK_LENGTH:
        chunks.append(chunk)
        return chunks
    chunks.extend(part for part in hard_split(chunk) if should_keep_chunk(part))
    return chunks


def should_keep_chunk(chunk: str) -> bool:
    if not chunk.strip():
        return False
    if len(chunk) >= MIN_CHUNK_LENGTH:
        return True
    return has_business_value(chunk)


def has_business_value(text: str) -> bool:
    business_keywords = ("价格", "报价", "元", "周期", "交付", "企业微信", "企微", "飞书", "售后", "维护", "基础版", "标准版", "高级版")
    return any(keyword in text for keyword in business_keywords) and len(text.strip()) >= 20


def build_chunk_content(original_filename: str, index: int, chunk: str) -> str:
    return f"来源文件：{original_filename}\n片段：{index}\n正文：{chunk.strip()}"
