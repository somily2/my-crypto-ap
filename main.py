import flet as ft
import requests
from datetime import datetime

def main(page: ft.Page):
    # إعدادات نافذة التطبيق العامة لتبدو كشاشة جوال
    page.title = "المحلل المالي المتقدم"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True  # دعم اللغة العربية والاتجاه من اليمين لليسار
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # متغير لحفظ سعر الصرف المجلوب
    usdt_rate_holder = [3.75]

    # دالة جلب سعر الصرف من فيزا بالخلفية
    def fetch_visa_rate():
        try:
            current_date = datetime.now().strftime("%m/%d/%Y")
            visa_url = f"https://www.visa.com.sa/cmsapi/fx/rates?amount=1&fromCurr=USD&toCurr=SAR&fee=0.0&date={current_date}"
            response = requests.get(visa_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            if response.status_code == 200:
                usdt_rate_holder[0] = float(response.json().get("fxRateWithAdditionalFee", 3.75))
                rate_badge.text = f"سعر صرف فيزا الحالي: 1 USD = {usdt_rate_holder[0]:.4f} SAR"
                page.update()
        except:
            rate_badge.text = "تم استخدام سعر الصرف الافتراضي: 1 USD = 3.75 SAR"
            page.update()

    # عناصر الواجهة الرسومية
    header_title = ft.Text("⇄ المحلل المالي الاحترافي", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    rate_badge = ft.Text("جاري تحديث سعر الصرف المباشر...", size=14, color=ft.colors.BLUE_200)
    
    amount_input = ft.TextField(
        label="المبلغ بالريال السعودي (SAR)",
        value="50",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.CENTER,
        border_color=ft.colors.BLUE_400,
        focused_border_color=ft.colors.BLUE_ACCENT,
        border_radius=10
    )
    
    results_container = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    # دالة الحساب المالي عند الضغط على الزر
    def calculate_finance(e):
        results_container.controls.clear()
        try:
            sar_amount = float(amount_input.value.strip())
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("الرجاء إدخال رقم صحيح!"))
            page.snack_bar.open = True
            page.update()
            return

        if sar_amount <= 0:
            return

        usdt_rate = usdt_rate_holder[0]
        p2p_fee_percentage = 0.002           
        fixed_fee_usdt = 0.5                 

        gross_usdt = sar_amount / usdt_rate
        fee_deducted_usdt = (gross_usdt * p2p_fee_percentage) + fixed_fee_usdt
        net_usdt = max(0.0, gross_usdt - fee_deducted_usdt)
        net_amount_in_sar = net_usdt * usdt_rate

        if sar_amount < 100:
            discount_amount_sar = max(0.0, sar_amount - net_amount_in_sar) + 11.5
            desc_card = "شاملة الرسوم + خصم البنك للمبالغ الصغيرة (11.5 ريال)"
            exchange_factor = ((sar_amount + 11.5) / net_usdt) if net_usdt > 0 else 0.0
            factor_color = ft.colors.RED_400
        else:
            discount_amount_sar = max(0.0, sar_amount - net_amount_in_sar)
            discount_percentage = (discount_amount_sar / sar_amount * 100)
            desc_card = f"نسبة الاقتطاع الكلي: {discount_percentage:.3f}%"
            exchange_factor = (sar_amount / net_usdt) if net_usdt > 0 else 0.0
            factor_color = ft.colors.PURPLE_300

        # بناء كروت عرض النتائج المتوافقة مع الجوال
        def make_card(title, value, subtitle, color):
            return ft.Container(
                content=ft.Column([
                    ft.Text(title, size=12, color=ft.colors.GREY_400),
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(subtitle, size=11, color=ft.colors.GREY_500),
                ], spacing=4),
                bgcolor=ft.colors.SURFACE_VARIANT,
                padding=15,
                border_radius=12,
                border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE))
            )

        results_container.controls.append(make_card("💰 رأس المال المستثمر بالدولار الرقمي", f"{gross_usdt:,.2f} USDT", "بناءً على سعر فيزا الفعلي", ft.colors.GREEN_400))
        results_container.controls.append(make_card("🛑 رسوم معالجة الصرف والمنصة", f"{fee_deducted_usdt:,.2f} USDT", "تأثير هيكل الرسوم (0.2% + 0.5$)", ft.colors.RED_400))
        results_container.controls.append(make_card("💵 الصافي الفعلي الجاهز للمحفظة", f"{net_usdt:,.2f} USDT", "السيولة الصافية المتاحة فوراً", ft.colors.BLUE_400))
        results_container.controls.append(make_card("📉 مقدار الحسم الكلي من الريال", f"{discount_amount_sar:,.2f} SAR", desc_card, ft.colors.ORANGE_400))
        
        # كرت السعر النهائي الحقيقي للعملية
        results_container.controls.append(
            ft.Container(
                content=ft.Text(f"سعر الصرف الفعلي الحقيقي = {exchange_factor:.3f}", size=15, weight=ft.FontWeight.BOLD, color=factor_color, text_align=ft.TextAlign.CENTER),
                bgcolor=ft.colors.BLACK45,
                padding=15,
                border_radius=10,
                alignment=ft.alignment.center
            )
        )
        page.update()

    calc_button = ft.ElevatedButton(
        text="⚙️ بدء المحاكاة والتحليل المالي",
        on_click=calculate_finance,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_600
        ),
        height=50
    )

    # إضافة العناصر للشاشة
    page.add(
        ft.VerticalDivider(height=10, color=ft.colors.TRANSPARENT),
        header_title,
        rate_badge,
        ft.VerticalDivider(height=15, color=ft.colors.TRANSPARENT),
        amount_input,
        ft.Row([calc_button], alignment=ft.MainAxisAlignment.CENTER),
        ft.VerticalDivider(height=10, color=ft.colors.TRANSPARENT),
        results_container
    )

    # تشغيل جلب البيانات فور فتح التطبيق
    fetch_visa_rate()

# لتشغيل التطبيق محلياً للتأكد منه
if __name__ == "__main__":
    ft.app(target=main)
