"""Regenerate fictional attachment PDFs. Requires reportlab."""
from pathlib import Path
from shutil import copy2
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FRONTEND = Path(__file__).resolve().parents[1]
OUTPUT = FRONTEND.parent / "output" / "pdf"
TARGET = FRONTEND / "assets" / "demo" / "media"
FONT = Path("/Library/Fonts/Arial Unicode.ttf")
BLUE, INK, GREY = "#3182F6", "#191F28", "#8B95A1"
pdfmetrics.registerFont(TTFont("KnoKorean", str(FONT)))
OUTPUT.mkdir(parents=True, exist_ok=True)
TARGET.mkdir(parents=True, exist_ok=True)


def text(pdf, x, y, value, size=11, color=INK):
    pdf.setFillColor(HexColor(color))
    pdf.setFont("KnoKorean", size)
    pdf.drawString(x, y, value)


def document(filename, title, subtitle):
    pdf = canvas.Canvas(str(OUTPUT / filename), pagesize=A4)
    pdf.setTitle(title)
    pdf.setAuthor("Kno demo")
    text(pdf, 48, 790, "크노 | 첨부자료", 12, BLUE)
    text(pdf, 48, 746, title, 23)
    text(pdf, 48, 716, subtitle, 10, GREY)
    pdf.setStrokeColor(HexColor("#E0E6ED"))
    pdf.line(48, 696, 547, 696)
    return pdf


def section(pdf, y, title, lines):
    text(pdf, 48, y, title, 14, BLUE)
    for i, line in enumerate(lines):
        text(pdf, 48, y - 29 - i * 23, line)
    return y - 70 - len(lines) * 23


def finish(pdf, filename):
    text(pdf, 48, 65, "이 문서는 화면 시연을 위한 가상 첨부자료입니다.", 9, GREY)
    text(pdf, 537, 65, "1", 9, GREY)
    pdf.save()
    copy2(OUTPUT / filename, TARGET / filename)


def ai_guide():
    name = "ai-challenge-guide.pdf"
    pdf = document(name, "대학생 AI 서비스 아이디어 공모전", "참가 안내 | 예시 문서")
    y = section(pdf, 657, "01  공모 주제", [
        "일상의 불편을 해결하는 AI 서비스 아이디어를 제안해 주세요.",
        "기획, 개발, 디자인 등 다양한 관점에서 참여할 수 있습니다."])
    y = section(pdf, y, "02  참가 방법", [
        "개인 또는 4인 이하 팀으로 참여합니다.",
        "신청자 이름, 안내받을 이메일, 포트폴리오 링크를 준비해 주세요."])
    section(pdf, y, "03  제출 준비", [
        "해결하려는 문제와 서비스 아이디어를 기획서에 정리합니다.",
        "기획서와 포트폴리오 링크를 온라인 신청서에 제출합니다.",
        "신청 기간과 세부 조건은 공고 본문에서 확인해 주세요."])
    finish(pdf, name)


def scholarship_form():
    name = "scholarship-form.pdf"
    pdf = document(name, "학습 성장 장학금 신청서", "지원 양식 | 예시 문서")
    labels = ["이름", "이메일", "학번", "학습 목표", "주요 학습 계획"]
    for i, label in enumerate(labels):
        y = 650 - i * 78
        text(pdf, 48, y, label, 12, BLUE)
        pdf.setStrokeColor(HexColor("#D1D6DB"))
        pdf.roundRect(48, y - 54, 499, 42, 6)
    text(pdf, 48, 215, "첨부 확인: 재학증명서", 11)
    text(pdf, 48, 186, "아래 내용은 개인정보를 입력하지 않은 빈 신청 양식입니다.", 10, GREY)
    finish(pdf, name)


def graduation_guide():
    name = "graduation-guide.pdf"
    pdf = document(name, "SW대학 졸업 프로젝트 설명회", "설명회 안내 | 예시 문서")
    y = section(pdf, 657, "01  대상", ["졸업 프로젝트를 준비하는 재학생을 위한 설명회입니다."])
    y = section(pdf, y, "02  주요 안내", [
        "프로젝트 주제 선정과 팀 구성 방법을 소개합니다.",
        "프로젝트 계획과 진행 과정에서 준비할 내용을 안내합니다."])
    section(pdf, y, "03  사전 신청", [
        "신청자 이름, 안내받을 이메일, 학과 및 학년을 확인해 주세요.",
        "신청 일정과 참여 방법은 공고 본문을 참고해 주세요."])
    finish(pdf, name)


ai_guide()
scholarship_form()
graduation_guide()
