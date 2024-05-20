from random import randint
from typing import Iterable

import google.generativeai as genai
import streamlit as st

COFFEE_BOT_PROMPT = """\Bạn là một hệ thống nhận order cà phê và bạn bị hạn chế chỉ nói về đồ uống trên MENU. Đừng bao giờ nói về bất cứ điều gì ngoài việc gọi MENU đồ uống cho khách hàng.
    Mục tiêu của bạn là thực hiện place_order sau khi hiểu rõ các mục trong menu và bất kỳ sửa đổi nào mà khách hàng muốn.
    Thêm các mặt hàng vào đơn đặt hàng của khách hàng bằng add_to_order, xóa các mặt hàng cụ thể bằng Remove_item và đặt lại đơn hàng bằng clear_order.
    Để xem nội dung của đơn hàng cho đến thời điểm này, hãy gọi get_order (theo mặc định, nội dung này được hiển thị cho bạn chứ không phải người dùng)
    Luôn xác nhận đơn hàng với thông tin đơn hàng trước khi gọi place_order. Xác nhận đơn hàng sẽ hiển thị các mục trong đơn hàng cho người dùng và trả về phản hồi của họ khi xem danh sách. Phản hồi của họ có thể chứa các sửa đổi.
    Luôn xác minh và phản hồi bằng tên đồ uống và tên bổ sung từ MENU trước khi thêm chúng vào đơn hàng.
    Nếu bạn không chắc đồ uống hoặc chất bổ sung có phù hợp với những thứ trên MENU hay không, hãy đặt câu hỏi để làm rõ hoặc chuyển hướng.
    Bạn chỉ có những bổ sung được liệt kê trong menu bên dưới: Tùy chọn sữa, cà phê espresso, caffeine, chất làm ngọt, yêu cầu đặc biệt.
    Sau khi khách hàng đã đặt hàng xong, hãy xác nhận đơn hàng rồi đặt_order.

    Giờ: Thứ Ba, Thứ Tư, Thứ Năm, 10 giờ sáng đến 2 giờ chiều
    Giá: trong menu dưới.


    MENU:

    Chè Hoa - Nước Dừa:
    Chè thập cẩm - 17.000đ
    Sương sa hạt lựu - 17.000đ
    Chè Chuối Híp - 17.000đ
    Chè đậu ván - 17.000đ
    Chè đậu đen - 17.000đ
    Chè bơ - 17.000đ
    Chè đậu trắng - 17.000đ
    Chè khoai - 17.000đ
    Chè dưa xanh dầm - 17.000đ
    Dưa Xanh Dừa - 20.000đ
    Chè dưa xanh - 17.000đ
    Sương sáo nước dừa - 17.000đ
    Chè trôi nước - 17.000đ

    Chè Hoa - Không Nước Dừa:
    Sâm bổ lượng - 17.000đ
    Bánh Flan - 17.000đ
    Chè bách quả - 17.000đ
    Ngọt dất sưa chua - 20.000đ
    Nếp cẩm sưa chua - 20.000đ
    Chè Củ Nắng - 17.000đ
    Chè xoài - 17.000đ
    Lá Xanh Hạt É - 17.000đ
    Xưa Xưa Quỳnh (1 Hộp) - 25.000đ

    Rau Câu - Chè Hoa:
    Rau câu thập cẩm - 17.000đ
    Rau câu dưa bánh flan - 17.000đ
    Rỉu dưa - 17.000đ

    Promo:
    Bánh Tráng Mắm Ruốc (Đặc Sản Gò Lá) - 17.000đ

    Tuỳ chỉnh:
    Đá: bỏ đá ngoài, bỏ sẵn đá bên trong (mặc định)
    Đường: 25% (ít), 50% (vừa), 75% (mặc định), 100% (nhiều)
    """


# Define the API


class OrderBot():
    def __init__(self, order=None, placed_order=None) -> None:
        self.order = [] if order is None else order
        self.placed_order = [] if placed_order is None else placed_order

    def add_to_order(self, drink: str, modifiers: Iterable[str] = []) -> None:
        """Adds the specified drink to the customer's order, including any modifiers."""
        self.order.append((drink, modifiers))

    def get_order(self) -> Iterable[tuple[str, Iterable[str]]]:
        """Returns the customer's order."""
        return self.order

    def remove_item(self, n: int) -> str:
        """Remove the nth (one-based) item from the order.

        Returns:
        The item that was removed.
        """
        item, modifiers = self.order.pop(int(n) - 1)
        return item

    def clear_order(self) -> None:
        """Removes all items from the customer's order."""
        self.order.clear()

    def place_order(self) -> int:
        """Submit the order to the kitchen.

        Returns:
        The estimated number of minutes until the order is ready.
        """
        self.placed_order[:] = self.order.copy()
        self.clear_order()

        # TODO(you!): Implement coffee fulfilment.
        return randint(1, 10)

    def start_chat(self, prompt=COFFEE_BOT_PROMPT, use_sys_inst=False):
        print('starting chat')
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

        ordering_system = [self.add_to_order, self.get_order, self.remove_item,
                           self.clear_order, self.place_order]

        model_name = 'gemini-1.5-pro-latest' if use_sys_inst else 'gemini-1.0-pro-latest'

        if use_sys_inst:
            model = genai.GenerativeModel(
                model_name, tools=ordering_system, system_instruction=prompt)
            convo = model.start_chat(enable_automatic_function_calling=True)

        else:
            model = genai.GenerativeModel(model_name, tools=ordering_system)
            convo = model.start_chat(
                history=[
                    {'role': 'user', 'parts': [prompt]},
                    {'role': 'model', 'parts': [
                        'OK I understand. I will do my best!']}
                ],
                enable_automatic_function_calling=True)

        return convo
