# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:HTHC
- Members:Lê Gia Hưng, Hà Minh Thắng, Nguyễn Thế Hoàng, Đặng Đức Cương
- Provider/model:OpenAI/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

AI & Tech Research Agent - một agent tổng hợp tin AI/công nghệ mỗi ngày từ web, Twitter, Hacker News, GitHub và Hugging Face, rồi xuất thành bản tin tiếng Việt.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: 

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | Lấy các bài đăng gần đây từ một tài khoản Twitter/X cụ thể. | không |
|social_search | Tìm bài đăng trên Twitter/X theo từ khóa, sắp xếp theo mới nhất (Latest) hoặc nổi bật (Top). |  không|
|lookup |	Tìm kiếm thông tin hoặc tin tức trên web trong một khoảng thời gian.|không|
|fetch|Đọc nội dung trang web từ một đường dẫn URL.|không|
|format|Trình bày thông tin đã thu thập thành bản tin tổng hợp, danh sách gạch đầu dòng, chuỗi bài đăng hoặc bản tin AI hằng ngày bằng tiếng Việt.|không|
|send|Gửi văn bản lên Telegram; cần người dùng xác nhận trước khi gửi.|không|
|policy|Tìm kiếm trong các tài liệu chính sách nội bộ được lưu cục bộ.|không|
|papers|Tìm kiếm bài báo nghiên cứu khoa học trên arXiv.|không|
|paper_text|Tải tệp PDF của bài báo trên arXiv và trích xuất nội dung văn bản.|không|
|google_maps|Tìm kiếm và gắn kèm link googlemap |Đúng|
|cite_sources|Gắn kèm nguồn gốc của tin |Đúng|

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.Hôm nay có những tin tức AI nào nổi bật nhất?

2.Những mô hình AI mới nào vừa được ra mắt?

3.Top 5 dự án AI đang trending trên GitHub là gì?

4.Cộng đồng Hacker News đang thảo luận về chủ đề AI nào?

5.Xu hướng công nghệ nào đang được quan tâm nhất tuần này?

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |Đo hành vi của prompt và tools.yaml starter trước khi sửa  |  | 0.70 |  runs/v0_B_base_openrouter_20261110T102735867300.json|
| v1 |  system_prompt.md| H1: thay chỉ dẫn đoán bằng rule gọi clarify khi thiếu account/URL, vẫn cho map tên người sang handle → R10, R11 PASS | 0.70 | 0.85 |runs/v1_B_base_openrouter_20261110T105843902795.json  |
| v2 | system_prompt.md | H3: thay cứ gửi luôn bằng rule xác nhận clarify yes_no trước khi send → R12 PASS. Kết quả: R12 vẫn FAIL (model hỏi nội dung bằng text, xung đột với rule thiếu thông tin của H1); chạy lại v2-rerun cho cùng kết quả |0.85  | 0.95 | runs/v2_B_base_openrouter_20261110T105932596003.json |
| v3 | system_prompt.md |H3b: thêm câu ưu tiên xác nhận yes_no hơn rule thiếu thông tin → R12 PASS. Kết quả: BÁC BỎ, R12 vẫn FAIL; R11 (thiếu response_type) và R13 (thiếu topic) dao động. Gỡ câu này, v4 xây trên v2  |0.95  | 0.85 | runs/v3_B_base_openrouter_20261110T110117470939.json |
|v4|tools.yaml|H6: viết lại tools.yaml: description có khi nào dùng / không dùng, convention args, response_type và topic thành required, clarify mô tả yes_no cho send → R11, R12, R13 PASS. Kết quả: 20/20, v4-rerun cũng 20/20|0.95|1.0|runs/v4_B_base_openrouter_20261110T110248937728.json|
|v4.5|system_prompt.md|Bỏ câu ép một bước thì base vẫn 20/20 (3/3 lần chạy)|1.0|1.0|runs/v4.5_B_base_openrouter_20261110T114843251934.json|

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
