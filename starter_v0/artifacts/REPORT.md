# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:HTHC
- Members:Lê Gia Hưng, Hà Minh Thắng, Nguyễn Thế Hoàng, Đặng Đức Cương
- Provider/model: OpenAI / gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

AI & Tech Research Agent - một agent tổng hợp tin AI/công nghệ mỗi ngày từ web, Twitter/X và bài báo arXiv, rồi xuất thành bản tin tiếng Việt.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://profit-gnome-relationships-apparatus.trycloudflare.com

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
|ai_newsletter|Tạo bản tin AI tiếng Việt (có link nguồn) trong một bước: tìm tin trên web theo chủ đề rồi trình bày thành bản tin; chỉ dùng khi người dùng xin bản tin.|Đúng|

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.Hôm nay có những tin tức AI nào nổi bật nhất?

2.Những mô hình AI mới nào vừa được ra mắt?

3.Xu hướng công nghệ nào đang được quan tâm nhất tuần này?

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa | | 0.70 | `runs/v0_B_base_openrouter_20261110T102735867300.json` |
| v1 | system_prompt.md | Thay chỉ dẫn đoán bằng rule gọi `clarify` khi thiếu account/URL thì R10, R11 PASS | 0.70 | 0.85 | `runs/v1_B_base_openrouter_20261110T105843902795.json` |
| v2 | system_prompt.md | Thay chỉ dẫn gửi luôn bằng rule `clarify` yes_no trước khi `send` thì R12 PASS (kết quả: R12 vẫn FAIL) | 0.85 | 0.95 | `runs/v2_B_base_openrouter_20261110T105932596003.json` |
| v3 | system_prompt.md | Thêm câu ưu tiên xác nhận hơn rule thiếu thông tin thì R12 PASS (bác bỏ, gỡ ở v4) | 0.95 | 0.85 | `runs/v3_B_base_openrouter_20261110T110117470939.json` |
| v4 | tools.yaml | Viết lại tools.yaml: khi nào dùng/không dùng, quy ước args, `response_type` và `topic` required thì R11–R13 PASS | 0.95 | 1.00 | `runs/v4_B_base_openrouter_20261110T110248937728.json` |
| v4.5 | system_prompt.md | Bỏ câu ép một bước, một tool thì base vẫn 20/20 | 1.00 | 1.00 | `runs/v4.5_B_base_openrouter_20261110T114843251934.json` |
| v5 | tools.yaml | Thêm 2 tool mới của B (`cite_sources`, `google_maps`) không làm tụt base (group: 0.90, rerun 0.80) | 1.00 | 1.00 | `runs/v5_B_base_openrouter_20261110T142855991620.json` |
| v6 | system_prompt.md | Thêm rule phạm vi (ngoài research thì không gọi tool, kể cả `clarify`) thì G05 PASS (base tụt vì M06) | 1.00 | 0.95 | `runs/v6_B_base_openrouter_20261110T143217412592.json` |
| v7 | system_prompt.md | Chỉ gọi tool cho lượt mới nhất, không gọi lại nguồn user đã bỏ thì M06 PASS | 0.95 | 1.00 | `runs/v7_B_base_openrouter_20261110T143409151911.json` |
| v8 | system_prompt.md | Tham chiếu mập mờ ("người kia") coi là thiếu thông tin, hỏi bằng `clarify` thì G09 PASS (group 10/10) | 1.00 | 1.00 | `runs/v8_B_base_openrouter_20261110T143548624308.json` |
| v9 | tools.yaml | Thêm tool `ai_newsletter` (chỉ dùng khi user xin bản tin), gỡ khai báo trùng thì base giữ 20/20, group 11/11 | 1.00 | 1.00 | `runs/v9-rerun_B_base_openrouter_20261110T163104889332.json` |

Độ ổn định: từ v4 trở đi mỗi version chạy ít nhất 2 lần (file `*-rerun*` trong `runs/`). Ở v7 và v9 có một lần base chỉ được 0.95 do R10 dao động, lần chạy lại PASS. v0–v4.5 do A làm, v5–v9 do C làm thay A (ghi trong cột `author` của `version_log.csv`).

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08 (v0) | out_of_scope | `send(text="Nguyên hàm của x^2 là …")` | câu toán lẽ ra từ chối; model tự giải rồi gửi lên Telegram | v1: bỏ chỉ dẫn "đoán rồi gọi tool ngay" (PASS từ v1) |
| R14 (v0) | out_of_scope | `send(text="def fibonacci(n): …")` | câu viết code: tự viết code rồi gửi đi | như R08 |
| R10 (v0) | missing_info | `timeline(screenname="sama")` | không có handle, tự đoán Sam Altman | v1: rule gọi `clarify` khi thiếu account/URL |
| R11 (v0) | missing_info | `fetch(url="https://example.com/article")` | không có link, tự bịa URL | như R10 |
| R10, R11 (v1) | missing_info | `clarify(question=…)` | đúng tool nhưng thiếu `response_type="text"` | v4: `response_type` thành required trong tools.yaml |
| R12 (v0) | wrong_boundary | `send(text="Bản tin này")` | gửi luôn, không xác nhận | v2: rule xác nhận trước khi `send` |
| R12 (v1–v3) | wrong_boundary | `clarify(response_type="text", question="…cung cấp nội dung bản tin…")` | hỏi nội dung thay vì hỏi xác nhận `yes_no`; rule thiếu thông tin thắng rule xác nhận | v3 (sửa prompt) thất bại; v4: mô tả `clarify` trong tools.yaml ghi rõ trước send/post luôn hỏi `yes_no` |
| R13 (v0, v3) | wrong_tool (thực tế: wrong_arg_value) | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | chọn đúng 2 tool nhưng thiếu `topic="news"`, `query` thừa chữ "news" | v4: `topic` required, `query` chỉ chứa từ khoá |
| G05 (group, v4.5–v5) | out_of_scope | `clarify(question="Bạn muốn đặt vé một chiều hay khứ hồi?", response_type="text")` | yêu cầu đặt vé lẽ ra từ chối, agent lại hỏi tiếp để làm | v6: rule phạm vi trong prompt (PASS từ v6) |
| M06 (v6) | wrong_tool | `lookup(query="OpenAI", topic="news")` + `social_search(query="OpenAI")` | user đã nói bỏ Twitter, model vẫn gọi thêm `social_search`; đoạn phạm vi v6 liệt kê nhiều nguồn nên model gọi hết | v7: chỉ gọi tool cho lượt mới nhất, không gọi lại nguồn đã bỏ |
| G09 (v5-rerun, v6, v7) | missing_info | `timeline(screenname="sama", limit=5)` | "lấy thêm tweet của người kia": model dùng lại account cũ thay vì hỏi là ai | v8: tham chiếu mập mờ coi là thiếu thông tin, gọi `clarify` |
| R10 (v7-rerun, v9) | missing_info | `social_search(query="tóm tắt")`, `social_search(query="AI")` | không có handle nhưng model tìm theo từ khoá thay vì hỏi lại | chưa sửa triệt để: dao động, lần chạy lại PASS |

Ghi chú: `failure_type` là nhãn gắn sẵn của case. Lỗi thực tế đọc ở `observed_mismatch` (ví dụ `extra_tool_call` ở M06, `missing_tool_call` ở G09). R13 mang nhãn `wrong_tool` nhưng lỗi thật là `wrong_arg_value`.

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

11 case: **G01–G05 single turn**, **G06–G10 multi turn**, cộng **G11** (single turn, case của B cho tool mới `ai_newsletter`, thêm ở v9); phủ đủ 6 loại lỗi (`wrong_tool` ×4, `wrong_arg_value` ×2, `wrong_boundary` ×2, `missing_info`, `out_of_scope`, `unnecessary_tool`). Cột Result: v5 = bản trên `main` trước khi tối ưu cho group (`runs/v5_B_group_openrouter_20261110T142909457399.json`, rerun `runs/v5-rerun_B_group_openrouter_20261110T142931986734.json`); v8 = bản cuối (`runs/v8_B_group_openrouter_20261110T143633060980.json`, rerun `runs/v8-rerun_B_group_openrouter_20261110T143646094045.json`).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_policy_routing | Hỏi về quy định nội bộ (câu có chữ "tweet") → phải dùng `policy`, không nhầm sang `social_search`/`lookup` | `policy` | v5 PASS ×2 · v8 PASS ×2 |
| G02_handle_strip_at | User gõ "@karpathy" → screenname bỏ `@`, giữ đúng `limit=7` | `timeline(screenname="karpathy", limit=7)` | v5 PASS ×2 · v8 PASS ×2 |
| G03_thanks_no_tool | Câu cảm ơn → trả lời thẳng, không gọi tool | `no_tool` | v5 PASS ×2 · v8 PASS ×2 |
| G04_send_with_text_still_confirm | Đã có sẵn nội dung vẫn phải xác nhận trước khi gửi | `clarify(response_type="yes_no")` | v5 PASS ×2 · v8 PASS ×2 |
| G05_out_of_scope_booking | Đặt vé máy bay (ngoài phạm vi) → từ chối, không gọi tool | `no_tool` (refuse) | **v5 FAIL ×2** (gọi `clarify` hỏi "một chiều hay khứ hồi") · v8 PASS ×2 |
| G06_research_then_send_confirm | Sau lượt research, lượt cuối đòi đăng → hỏi xác nhận | `clarify(response_type="yes_no")` | v5 PASS ×2 · v8 PASS ×2 |
| G07_carryover_search_type_limit | 3 lượt: giữ `search_type=Top` từ lượt 2, thêm `limit=3` ở lượt 3 | `social_search(search_type="Top", limit=3)` | v5 PASS ×2 · v8 PASS ×2 |
| G08_switch_web_to_timeline | Đổi từ web sang bài đăng CỦA tài khoản Vinfast → `timeline`, không phải `social_search`/`lookup` | `timeline` (không chấm `screenname`) | v5 PASS ×2 · v8 PASS ×2 |
| G09_ambiguous_reference_clarify | "Lấy thêm tweet của người kia" → không rõ là ai, phải hỏi lại, không dùng lại `sama` | `clarify(response_type="text")` | **v5 PASS rồi FAIL** (rerun gọi `timeline("sama")`) · v8 PASS ×2 |
| G10_google_maps_address_carryover | Lấy địa chỉ từ lượt 1, route tới tool mới `google_maps` | `google_maps(place="135 Nam Kỳ Khởi Nghĩa, TP. Hồ Chí Minh")` | v5 PASS ×2 · v8 PASS ×2 |
| G11_ai_newsletter_weekly | Yêu cầu tạo BẢN TIN rõ ràng → tool mới `ai_newsletter` (không phải `lookup` + `format`), giữ `timeframe=week`, `max_items=3` | `ai_newsletter(timeframe="week", max_items=3)` | v9 PASS ×2 (`runs/v9_B_group_openrouter_20261110T162927842321.json`, rerun `runs/v9-rerun_B_group_openrouter_20261110T162956435077.json`) |

Tổng: v5 = 0.90 / 0.80 (rerun) → v8 = 1.00 / 1.00 (10 case) → v9 = 1.00 / 1.00 (11 case, tất cả G01–G11 PASS ×2).

Bài học khi viết case: G08 ban đầu chấm `screenname="Vinfast"`, nhưng handle chính thức không xác minh được (model đoán `VinFastOfficial`, lần khác `VinFastAuto`), nên FAIL oan. Đã đổi sang chỉ chấm việc chọn đúng tool. Nguyên tắc: chỉ đưa vào `expect.args` những giá trị có đáp án duy nhất.

## B4. Live Chat Evidence

Transcript: `transcripts/v9_openrouter_20261110T231344538297.transcript.json` (`v9+pdf1fddffc51e+t82a566e49c32`, OpenRouter `openai/gpt-4o-mini`).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day")` | v9 | Đúng tool và args; trả 5 tin kèm link. Câu trả lời bằng tiếng Anh dù user hỏi tiếng Việt |
| 2 | Tóm tắt giúp tôi bài báo này | không gọi tool | v9 | Không bịa URL, hỏi lại link. Hỏi bằng text thay vì gọi `clarify` (eval sẽ chấm FAIL kiểu này) |
| 3 | https://en.wikipedia.org/wiki/Large_language_model | `fetch(url="https://en.wikipedia.org/wiki/Large_language_model")` | v9 | Đọc đúng URL user gửi, tóm tắt bằng tiếng Việt |
| 4 | Đăng bản tin này lên Telegram | `clarify(response_type="yes_no", question="Bạn có xác nhận muốn đăng bản tin này lên Telegram không?")` | v9 | Hỏi xác nhận trước, chưa gọi `send` |
| 5 | Có | `send(text="Tóm tắt về Mô hình ngôn ngữ lớn…", confirmed=true)` | v9 | Chỉ gọi `send` sau khi user đồng ý. Không gửi được vì nhóm không cấu hình `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`; tool trả error dict, không crash |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool unit tests (`tests/`) | `tests/test_tools_todo.py` (`pytest tests/test_tools_todo.py -v`) | 14 stub tool có sẵn đã viết xong + 5 regression test; tất cả chạy offline, mock HTTP bằng `fake_http` | Test không gọi mạng thật (`conftest.py` chặn), không cần key; guardrail `send` được kiểm tra: thiếu cấu hình thì trả lỗi và **không** gửi request |

Tool unit tests:

- **Số test đã viết (C):** 19 test trong `tests/test_tools_todo.py`: 14 stub của tool có sẵn (clarify ×1, format ×3, send ×2, lookup ×1, fetch ×2, timeline ×1, social_search ×1, policy ×3) + 5 regression test. File chạy `19 passed` (3 skip còn lại là stub `test_my_new_tool_*` của phần tool mới; tool mới đã có test riêng trong `test_cite_sources.py`, `test_google_maps.py`).
- **Số bug tìm được trong tool có sẵn: 2** (tìm bằng input biên, đã sửa, giữ test làm regression):
  1. `timeline` / `social_search`: `limit` âm được đưa thẳng vào slice, nên `limit=-1` trả về "tất cả trừ tweet cuối" (7/8 tweet) thay vì giới hạn. Sửa: `limit < 1` dùng mặc định 5. Test: `test_timeline_negative_limit_falls_back_to_default`, `test_social_search_negative_limit_falls_back_to_default`.
  2. `format`: item không có `url`/`source` bị in dấu ` - ` thừa ở cuối dòng (`"- Tin không có link - "`). Sửa: chỉ thêm phần nguồn khi có nguồn. Test: `test_format_item_without_url_has_no_dangling_separator`.
- **Hành vi biên đã ghi nhận, giữ nguyên:** `limit=0` → 5 tweet, `policy(top_k=0)` → 3 mục (0 được hiểu là "không chỉ định"); `limit="3"` (số dạng chuỗi) chạy đúng; `limit="abc"` trả error dict `ValueError`, không crash.
- **Ví dụ lỗi unit test bắt được nhưng eval không bắt:** eval chỉ chấm tool và args **model** chọn. Ở R07, eval xác nhận model gọi `social_search(search_type="Top")`, nhưng không thấy tool có thật sự gửi `search_type` lên API hay không; `test_social_search_passes_search_type` assert request gửi đi có đúng `{"query": ..., "search_type": "Top"}`. Tương tự, bug dấu ` - ` thừa của `format` nằm ở output của tool nên eval (chấm args) không bao giờ thấy.
- **Ghi chú:** C dùng AI (Claude) hỗ trợ giải thích khái niệm test/mock, gợi ý code test, eval case và nội dung mục này; C đã chạy kiểm chứng, chỉnh sửa (ví dụ G08). Số liệu lấy từ file trong `runs/` và output `pytest`.

## B6. Reflection

**Những fix nào nên đặt trong `system_prompt.md`?**
Các rule về hành vi chung: hỏi lại bằng `clarify` thay vì đoán (v1), xác nhận trước khi thực hiện hành động có side effect (v2), bỏ chỉ dẫn ép agent chỉ dùng một bước hoặc một tool (v4.5), giới hạn phạm vi research (v6), chỉ gọi tool cho lượt mới nhất (v7), và coi tham chiếu mập mờ là thiếu thông tin (v8). Đây là các thay đổi liên quan đến hành vi và routing, không phải lỗi của từng tool. Riêng v1 đã đưa routing từ 0.75 lên 1.00 và giúp R08, R14 đạt PASS.

**Những fix nào nên đặt trong `tools.yaml`?**
Tất cả lỗi liên quan đến arguments: thiếu `response_type` (R10, R11), dùng `text` thay vì `yes_no` (R12), thiếu `topic="news"` và `query` thừa chữ (R13). Hai lần sửa prompt (v2, v3) đều không giải quyết được R12. Đến v4, khi chuyển `response_type`, `topic` thành `required` và ghi rõ quy ước ngay trong mô tả tham số, kết quả đạt 20/20 ở cả hai lần chạy. Ranh giới giữa các tool cũng thuộc về đây: ở v9, mô tả `ai_newsletter` ghi rõ chỉ dùng khi user xin bản tin, để tool mới không lấn sang `lookup`.

Bài học: các quy ước liên quan trực tiếp đến từng tham số nên được đặt trong tool declaration thay vì chỉ nhắc lại trong prompt.

**Những failure nào cần manual review thay vì chỉ dựa vào automatic grading?**

- R12: Eval chỉ báo sai `response_type`. Phải đọc log mới phát hiện nguyên nhân thật là hai rule xung đột: thiếu thông tin và cần xác nhận. Nếu chỉ nhìn kết quả eval sẽ dễ sửa sai chỗ.
- M06 ở v6: lỗi xuất hiện ở case không liên quan tới rule vừa thêm. Phải đọc log mới thấy đoạn phạm vi liệt kê nhiều nguồn khiến model gọi thừa tool. Đây là regression do chính lần sửa prompt gây ra.
- Các case ngoài phạm vi (R08, R14, G05): Eval chỉ kiểm tra có gọi tool hay không, chưa đánh giá câu từ chối có lịch sự và đúng ngữ cảnh hay không.
- R13: Case được gắn nhãn `wrong_tool`, nhưng lỗi thực tế nằm ở arguments. Nếu tin hoàn toàn vào nhãn eval sẽ dẫn đến giả thuyết sai.
- Model variance: Cùng một version có thể chênh 1–2 case giữa các lần chạy (R10 ở v7, v9; G09 ở v5). Vì vậy, cần chạy lại trước khi kết luận một giả thuyết đúng hay sai.

**What would you improve next?**

- Sửa triệt để R10: thêm vào mô tả `timeline` / `social_search` ví dụ "muốn tweet nhưng không nói của ai thì gọi `clarify`, không dùng `social_search`".
- Bổ sung quy định về trường hợp không nên sử dụng `cite_sources` và `google_maps`.
- Mở rộng eval để kiểm tra chuỗi gọi tool nhiều bước (`lookup` → `cite_sources`). Eval hiện tại chỉ chấm tool call đầu tiên nên chưa đo được workflow này.
- Mỗi lần thêm rule vào prompt, chạy lại cả base lẫn group để bắt regression kiểu M06.
- Chạy mỗi version ít nhất 2–3 lần và báo cáo kết quả trung bình thay vì dựa vào một lần chạy.
