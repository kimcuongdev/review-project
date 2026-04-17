import json

import streamlit as st

st.set_page_config(page_title="Quiz Demo", layout="wide")


# ----------------- HÀM CHẤM ĐIỂM -----------------
def grade_exam(questions):
    detail_scores = []
    total_score = 0.0

    for i, q in enumerate(questions):
        q_type = q.get("type", "single")
        options = q["options"]
        explanations = q.get("explanations", [])
        correct = set(q["correct_answers"])  # danh sách index đáp án đúng
        q_id = q.get("id", i + 1)

        if q_type == "single":
            # radio trả về chính chuỗi option
            user_choice = st.session_state.get(f"q_{i}")
            if user_choice is None:
                score = 0.0
                user_indices = []
            else:
                user_idx = options.index(user_choice)
                user_indices = [user_idx]
                score = 1.0 if user_idx in correct else 0.0

        else:  # multiple
            selected_indices = []
            for j, _ in enumerate(options):
                if st.session_state.get(f"q_{i}_opt_{j}", False):
                    selected_indices.append(j)

            user_indices = selected_indices
            true_selected = len(correct.intersection(selected_indices))
            false_selected = len(set(selected_indices) - correct)

            # mỗi câu multiple tối đa 1 điểm
            if len(correct) > 0:
                raw = (true_selected - false_selected) / len(correct)
            else:
                raw = 0.0
            score = max(0.0, raw)

        total_score += score
        detail_scores.append(
            {
                "id": q_id,
                "question": q["question"],
                "type": q_type,
                "options": options,
                "explanations": explanations,
                "score": score,
                "user_indices": user_indices,
                "correct_indices": list(correct),
            }
        )

    return total_score, detail_scores


def clear_answers():
    # Xoá toàn bộ key q_* trong session_state khi load đề mới
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith("q_")]
    for k in keys_to_delete:
        del st.session_state[k]
    if "last_result" in st.session_state:
        del st.session_state["last_result"]


# ----------------- GIAO DIỆN NHẬP JSON -----------------
st.title("Exam Questions - Streamlit Demo")

st.markdown("### Bước 1. Nhập JSON đề thi")

example_json = r"""
[
  {
    "id": 1,
    "question": "Đâu là đặc trưng của phương pháp LightGCN?",
    "type": "multiple",
    "options": [
      "Loại bỏ biến đổi phi tuyến trong GCN.",
      "Loại bỏ liên kết tự kết nối của đỉnh tới chính nó của GCN ban đầu.",
      "LightGCN chỉ sử dụng biểu diễn của user và item ở tầng cuối cùng của GCN để đưa ra dự đoán khả năng tương tác giữa chúng.",
      "LightGCN kết hợp biểu diễn tuyến tính của user và item ở nhiều tầng trong GCN để thu được biểu diễn cuối cùng."
    ],
    "explanations": [
      "ĐÚNG. LightGCN đơn giản hóa mạng GCN bằng cách loại bỏ các hàm kích hoạt phi tuyến (như ReLU) và các ma trận biến đổi đặc trưng (weight matrices). Các tác giả lập luận rằng hai thành phần này không mang lại lợi ích cho bài toán lọc cộng tác (Collaborative Filtering) mà chỉ làm tăng độ phức tạp tính toán.",
      "ĐÚNG. Trong công thức lan truyền (propagation) của LightGCN, embedding của một đỉnh ở lớp tiếp theo chỉ được tổng hợp từ các hàng xóm của nó mà không cộng thêm embedding của chính nó (self-connection) như trong GCN tiêu chuẩn. Thông tin bản thân đỉnh được bảo toàn thông qua cơ chế kết hợp lớp ở bước cuối cùng.",
      "SAI. LightGCN không chỉ sử dụng lớp cuối cùng. Việc chỉ dùng lớp cuối cùng thường dẫn đến hiện tượng 'over-smoothing' (quá mịn), làm mất đi tính đặc trưng riêng của từng user/item. LightGCN khắc phục điều này bằng cách kết hợp tất cả các lớp lại với nhau.",
      "ĐÚNG. LightGCN tính toán embedding cuối cùng (final representation) bằng cách lấy tổng có trọng số (weighted sum) hoặc trung bình của các embedding tại tất cả các lớp (từ lớp 0 đến lớp K). Việc này giúp mô hình nắm bắt được các kết nối ở nhiều bậc khác nhau."
    ],
    "correct_answers": [
      0,
      1,
      3
    ]
  },
  {
    "id": 2,
    "question": "Gợi ý phiên phù hợp cho hoàn cảnh nào?",
    "type": "multiple",
    "options": [
      "Khi hệ thống khó định danh user, chỉ có thông tin tương tác trong một phiên làm việc",
      "Trong các hệ thống ưu tiên quan tâm đến các sở thích ngắn hạn",
      "Khi quan tâm đến sở thích dài hạn của user",
      "Khi muốn học biểu diễn của user",
      "Khi muốn sử dụng thông tin từ tri thức lĩnh vực hoặc gợi ý item tương tự dựa trên thuộc tính"
    ],
    "explanations": [
      "ĐÚNG. Đây là trường hợp sử dụng điển hình nhất của Session-based RS (Gợi ý dựa trên phiên). Trong nhiều ngữ cảnh (ví dụ: thương mại điện tử, tin tức), người dùng thường không đăng nhập (anonymous users). Hệ thống không có lịch sử quá khứ mà chỉ có chuỗi hành động (clicks, views) trong phiên hiện tại để dự đoán ý định.",
      "ĐÚNG. Session-based RS tập trung vào việc nắm bắt \"sở thích ngắn hạn\" (short-term preferences) hoặc ý định tức thời của người dùng. Sở thích của người dùng có thể thay đổi rất nhanh tùy thuộc vào ngữ cảnh hiện tại (ví dụ: hôm nay mua quà tặng, ngày mai mua cho bản thân), do đó dữ liệu phiên hiện tại quan trọng hơn lịch sử dài hạn.",
      "SAI. Việc quan tâm đến sở thích dài hạn (long-term preferences) thường là mục tiêu của các hệ thống Lọc cộng tác (Collaborative Filtering) truyền thống hoặc các mô hình lai (Hybrid), nơi hồ sơ người dùng được xây dựng qua thời gian dài.",
      "SAI. Session-based RS chủ yếu học biểu diễn của \"phiên làm việc\" (session representation) hiện tại để dự đoán hành động tiếp theo. Do thường làm việc với người dùng ẩn danh, việc học một biểu diễn định danh cố định cho user không phải là mục tiêu chính.",
      "SAI. Đây là đặc điểm chính của hệ thống Gợi ý dựa trên nội dung (Content-based) hoặc Gợi ý dựa trên tri thức (Knowledge-based). Session-based RS dựa chủ yếu vào thứ tự chuỗi tương tác (sequential patterns) hơn là sự tương đồng về thuộc tính tĩnh của sản phẩm."
    ],
    "correct_answers": [
      0,
      1
    ]
  },
  {
    "id": 3,
    "question": "Tại sao cần gợi ý dựa trên tri thức?",
    "type": "multiple",
    "options": [
      "Giải quyết được vấn đề các items có số lượng đánh giá ít?",
      "Phù hợp hơn khi lịch sử tương tác đã quá cũ",
      "Khách hàng muốn định nghĩa rõ nhu cầu của họ một cách rõ ràng",
      "Gợi ý tìm ra các sản phẩm tương tự",
      "Gợi ý có tính cộng đồng cao"
    ],
    "explanations": [
      "ĐÚNG. Các hệ thống gợi ý thông thường (như Lọc cộng tác - CF) dựa vào lượng lớn dữ liệu đánh giá (rating) để tìm ra quy luật. Khi các item có ít hoặc không có đánh giá (Cold-start item), CF sẽ thất bại. Gợi ý dựa trên tri thức không phụ thuộc vào đánh giá của cộng đồng mà dựa vào sự khớp (matching) giữa đặc tính sản phẩm và yêu cầu người dùng, nên nó giải quyết tốt vấn đề khan hiếm dữ liệu đánh giá.",
      "ĐÚNG. Sở thích của người dùng có thể thay đổi theo thời gian. Dữ liệu lịch sử quá cũ có thể không còn phản ánh đúng nhu cầu hiện tại (ví dụ: 5 năm trước mua đồ chơi, nay muốn mua laptop). Gợi ý dựa trên tri thức cho phép người dùng nhập nhu cầu *tại thời điểm hiện tại* thay vì phỏng đoán dựa trên quá khứ lỗi thời.",
      "ĐÚNG. Đây là đặc điểm cốt lõi của Knowledge-based RS (thường là dạng Conversation hoặc Search-based). Người dùng đóng vai trò chủ động đưa ra các ràng buộc (constraints) cụ thể (ví dụ: \"Tôi cần một chiếc xe dưới 500 triệu, màu đỏ\"). Hệ thống này cần thiết khi người dùng có những yêu cầu phức tạp mà không thể suy diễn ngầm từ hành vi quá khứ.",
      "SAI. Việc tìm ra \"sản phẩm tương tự\" (dựa trên thuộc tính) là đặc trưng chính của phương pháp Content-based Filtering (Lọc dựa trên nội dung), hoặc Item-based Collaborative Filtering, không phải là lý do chính để chọn Knowledge-based.",
      "SAI. \"Tính cộng đồng cao\" là đặc điểm của Collaborative Filtering (Lọc cộng tác), nơi hệ thống dựa vào đám đông (neighbors) để đưa ra gợi ý. Gợi ý dựa trên tri thức mang tính cá nhân hóa dựa trên logic và luật (rules), không phụ thuộc vào cộng đồng."
    ],
    "correct_answers": [
      0,
      1,
      2
    ]
  },
  {
    "id": 4,
    "question": "Đâu là đặc trưng của thuật toán ITE (Implicit to Explicit model) khi khai thác đồng thời cả dữ liệu implicit và explicit feedback?",
    "type": "multiple",
    "options": [
      "Mỗi loại hành vi được biểu diễn dưới dạng ma trận cỡ MxN (số lượng user x số lượng item), với giá trị mỗi phần tử là giá trị nhị phân.",
      "Các loại hành vi có tính thứ tự từ thấp đến cao, trong đó hành vi cuối cùng được gọi là hành vi mục tiêu.",
      "Sử dụng các khối kiến trúc song song giữa các kiểu tương tác",
      "Sử dụng các khối kiến trúc nối tiếp để bắt thứ tự giữa các kiểu tương tác"
    ],
    "explanations": [
      "ĐÚNG. Trong ITE, dữ liệu đầu vào được tổ chức thành các ma trận tương tác riêng biệt cho từng loại hành vi (ví dụ: xem, click, mua). Vì dữ liệu thường là implicit (hành vi ẩn), nên giá trị thường được biểu diễn dưới dạng nhị phân (1 là có tương tác, 0 là không) để đơn giản hóa việc mô hình hóa sự xuất hiện của hành vi.",
      "ĐÚNG. ITE hoạt động dựa trên giả định về \"chuỗi hành vi\" (behavior chain) hoặc phễu chuyển đổi. Các hành vi không độc lập mà có thứ tự mức độ quan tâm tăng dần (ví dụ: View -> Add to Cart -> Buy). Mô hình tận dụng thông tin từ các hành vi mức thấp để hỗ trợ dự đoán hành vi mức cao (hành vi mục tiêu).",
      "SAI. Kiến trúc song song (parallel) thường ám chỉ việc xử lý các luồng thông tin một cách độc lập và chỉ gộp lại ở cuối. Tuy nhiên, đặc trưng của ITE là mô hình hóa mối quan hệ phụ thuộc/chuyển đổi giữa các hành vi, nên kiến trúc song song không phản ánh đúng bản chất \"từ Implicit sang Explicit\".",
      "ĐÚNG. Để mô hình hóa sự chuyển đổi từ hành vi mức thấp lên hành vi mức cao (như từ View sang Buy), ITE sử dụng kiến trúc nối tiếp (sequential/cascading). Đầu ra hoặc các đặc trưng học được từ tầng hành vi trước (implicit) sẽ được đưa vào làm tham số đầu vào cho tầng hành vi sau (explicit), giúp \"dẫn dắt\" việc học biểu diễn tốt hơn."
    ],
    "correct_answers": [
      0,
      1,
      3
    ]
  },
  {
    "id": 5,
    "question": "Chọn phát biểu CHÍNH XÁC nhất về kiến trúc và cơ chế hoạt động của mô hình NeuMF (Neural Matrix Factorization).",
    "type": "single",
    "options": [
      "NeuMF bắt buộc hai nhánh GMF (Generalized Matrix Factorization) và MLP (Multi-Layer Perceptron) phải chia sẻ chung một tập embedding (shared embeddings) để giảm thiểu số lượng tham số cần học.",
      "NeuMF kết hợp hai luồng riêng biệt: GMF để mô hình hóa tương tác tuyến tính và MLP để mô hình hóa tương tác phi tuyến, sau đó nối (concatenate) vector đầu ra của chúng trước lớp dự đoán cuối cùng.",
      "Trong NeuMF, nhánh GMF sử dụng hàm kích hoạt phi tuyến (như ReLU) ngay sau phép nhân từng phần (element-wise product) để tăng khả năng biểu diễn.",
      "NeuMF thay thế hoàn toàn phép nhân vô hướng (dot product) truyền thống bằng mạng MLP sâu và không còn giữ lại thành phần Matrix Factorization nào."
    ],
    "explanations": [
      "SAI, vì mặc dù có thể chia sẻ embedding, nhưng để đạt hiệu suất tối ưu và linh hoạt (flexibility), NeuMF thường sử dụng hai tập embedding riêng biệt cho GMF và MLP để chúng có thể học các đặc trưng trong các không gian khác nhau.",
      "ĐÚNG, đây là đặc điểm cốt lõi của NeuMF. Nó tổng quát hóa Matrix Factorization (thông qua GMF) và sử dụng mạng nơ-ron sâu (MLP) để học các tương tác phức tạp, tận dụng ưu điểm của cả hai.",
      "SAI, nhánh GMF trong NeuMF giữ nguyên tính chất tuyến tính của MF bằng cách sử dụng phép nhân từng phần (element-wise product) và trọng số tuyến tính ở lớp cuối, không chèn hàm kích hoạt phi tuyến giữa chừng.",
      "SAI, NeuMF là sự kết hợp (fusion) giữa GMF và MLP, nó vẫn giữ lại thành phần GMF (tương đương với MF truyền thống) chứ không loại bỏ hoàn toàn."
    ],
    "correct_answers": [
      1
    ]
  },
  {
    "id": 6,
    "question": "Dựa trên cơ chế của Lọc cộng tác sử dụng các phương pháp học máy cơ bản (như Naïve Bayes, Cây quyết định, Mạng nơ-ron), phát biểu nào sau đây là SAI?",
    "type": "single",
    "options": [
      "Mỗi user được biểu diễn như một mẫu dữ liệu (data instance), trong đó các chiều (dimensions) hoặc đặc trưng (features) chính là các items.",
      "Hệ thống chỉ cần huấn luyện một mô hình phân loại (classifier) duy nhất để dự đoán rating cho tất cả các items trong hệ thống.",
      "Điểm khác biệt so với mô hình truyền thống là bất kỳ thuộc tính (item) nào cũng có thể đóng vai trò là nhãn (label) cần dự đoán.",
      "Đối với Lọc cộng tác dựa trên Naïve Bayes, mặc dù thường áp dụng cho dữ liệu feedback rời rạc, nhưng có thể mở rộng cho dữ liệu liên tục bằng cách sử dụng Gaussian Naïve Bayes."
    ],
    "explanations": [
      "Đúng. Ý tưởng cơ bản là 'Biểu diễn user là các vector mà mỗi chiều là các items' và 'Xem xét user như data instance với các features là items'.",
      "Sai. Đây là phát biểu sai. 'Số lượng bộ phân loại bằng số lượng items'. Đối với cây quyết định hoặc mạng nơ-ron, ta cũng 'Phải xây dựng số lượng cây quyết định hoặc mạng nơ-ron nhân tạo bằng số lượng items'. Mỗi item cần một mô hình riêng để dự đoán giá trị cho nó.",
      "Đúng. Mỗi thuộc tính (item) đều có thể là thuộc tính nhãn, bất kỳ feature nào cũng có thể là label.",
      "Đúng. Áp dụng khi dữ liệu user-item feedback rời rạc (có thể mở rộng với user-item feedback liên tục với Gaussian Naïve Bayes)."
    ],
    "correct_answers": [
      1
    ]
  }
]

""".strip()

json_text = st.text_area(
    "Danh sách câu hỏi (JSON). Mỗi phần tử là một object gồm các trường: "
    "`id`, `question`, `type` ('single' hoặc 'multiple'), `options` (list các đáp án), "
    "`correct_answers` (list index đáp án đúng, bắt đầu từ 0).",
    value=example_json,
    height=300,
)

col_load, col_info = st.columns([1, 3])
with col_load:
    load_btn = st.button("Tải đề thi / Cập nhật")

with col_info:
    st.caption("✅ Bạn có thể sửa JSON ở bên trên rồi bấm **Tải đề thi** để cập nhật.")

if "questions" not in st.session_state:
    st.session_state["questions"] = None

if load_btn:
    try:
        questions = json.loads(json_text)
        assert isinstance(questions, list), "JSON phải là một list các câu hỏi."
        # kiểm tra sơ bộ cấu trúc
        for q in questions:
            for field in ["question", "options", "correct_answers"]:
                assert field in q, f"Thiếu trường '{field}' trong một câu hỏi."
        st.session_state["questions"] = questions
        clear_answers()
        st.success("Đã tải đề thi thành công!")
    except Exception as e:
        st.session_state["questions"] = None
        st.error(f"Lỗi khi đọc JSON: {e}")


# ----------------- GIAO DIỆN LÀM BÀI -----------------
questions = st.session_state.get("questions")

if questions:
    st.markdown("---")
    st.markdown("### Bước 2. Làm bài thi")

    # layout chia 2 cột giống hình: trái là danh sách số câu, phải là nội dung
    col_nav, col_exam = st.columns([1, 3])

    with col_nav:
        st.markdown("#### Câu hỏi")
        n = len(questions)
        cols = st.columns(5)
        for idx in range(n):
            col = cols[idx % 5]
            with col:
                st.button(f"{idx+1}", key=f"nav_{idx}", help=f"Question {idx+1}")

    with col_exam:
        st.subheader("Exam Questions")

        # hiển thị từng câu
        for i, q in enumerate(questions):
            st.markdown(f"**Question {q.get('id', i+1)}.** {q['question']}")
            q_type = q.get("type", "single")
            options = q["options"]

            if q_type == "single":
                st.radio(
                    "Chọn **một** đáp án:",
                    options,
                    key=f"q_{i}",
                    index=None,
                )
            else:
                st.write("Chọn **nhiều** đáp án (checkbox):")
                for j, opt in enumerate(options):
                    st.checkbox(opt, key=f"q_{i}_opt_{j}")
            st.markdown("---")

        submit_btn = st.button("Nộp bài thi")

        if submit_btn:
            total_score, detail_scores = grade_exam(questions)
            st.session_state["last_result"] = {
                "total": total_score,
                "detail": detail_scores,
                "max_score": len(questions),  # mỗi câu tối đa 1 điểm
            }

        # luôn hiển thị kết quả gần nhất nếu có
        if "last_result" in st.session_state:
            res = st.session_state["last_result"]
            st.markdown("## Kết quả")
            st.write(
                f"Điểm tổng: **{res['total']:.2f} / {res['max_score']}** "
                f"({res['total'] / res['max_score'] * 100:.1f}%)"
            )

            st.markdown("### Chi tiết từng câu (kèm đề và đáp án)")
            for d in res["detail"]:
                st.markdown(f"#### Câu {d['id']} – điểm: **{d['score']:.2f}**")
                st.markdown(d["question"])

                # hiển thị từng đáp án với icon trực quan
                for idx, opt in enumerate(d["options"]):
                    is_correct = idx in d["correct_indices"]
                    is_chosen = idx in d["user_indices"]

                    if is_correct and is_chosen:
                        prefix = "✅"  # đúng và bạn chọn
                        note = " **(bạn chọn, đáp án đúng)**"
                    elif is_correct and not is_chosen:
                        prefix = "☑️"  # đúng nhưng không chọn
                        note = " **(đáp án đúng, bạn bỏ sót)**"
                    elif (not is_correct) and is_chosen:
                        prefix = "❌"  # sai nhưng bạn chọn
                        note = " **(bạn chọn sai)**"
                    else:
                        prefix = "▫️"  # sai và không chọn
                        note = ""

                    st.markdown(f"{prefix} {opt}{note}")
                    # show explanation for this option if provided in question data
                    explanations = d.get("explanations", [])
                    if idx < len(explanations) and explanations[idx]:
                        st.caption(explanations[idx])

                st.markdown("---")
else:
    st.info("Hãy nhập JSON đề thi và bấm **Tải đề thi / Cập nhật** để bắt đầu làm bài.")
