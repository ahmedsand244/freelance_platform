from google import genai
from google.genai import types
from django.conf import settings

# System instruction prompt setting the context
SYSTEM_INSTRUCTION = """
أنت مساعد ذكي ولطيف لموقع (توركي - Torky) للخدمات المصغرة.
مهمتك الأساسية هي مساعدة المستخدمين في تصفح الموقع والبحث عن الخدمات المناسبة لهم.
الخدمات المعروضة في موقع توركي تشبه وتنافس خدمات (خمسات وفايفر) مثل:
البرمجة، التصميم، الكتابة والترجمة، السيو، التسويق الإلكتروني، وغيرها من الخدمات المصغرة المصممة لمساعدة الأفراد والشركات الصغيرة.
يجب أن تكون ردودك قصيرة، ودقيقة، وودودة باللغة العربية، وألا تجيب على أسئلة خارج سياق الخدمات المصغرة وموقع توركي.
"""

def get_chatbot_response(user_message):
    try:
        api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
        if not api_key:
            return "عذراً، نظام المحادثة غير مفعل حالياً (مفتاح API مفقود)."

        client = genai.Client(api_key=api_key)

        # gemini-2.0-flash-lite متاح على الـ Free Tier بشكل كامل
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
            contents=user_message,
        )

        if response and response.text:
            return response.text
        else:
            return "عذراً، لم أتمكن من فهم طلبك في الوقت الحالي. هل يمكنك إعادة صياغته؟"

    except Exception as e:
        error_str = str(e)
        if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
            return "عذراً، تجاوزنا الحد المسموح من الطلبات حالياً. يرجى المحاولة بعد دقيقة."
        import traceback
        traceback.print_exc()
        return "يوجد مشكلة تقنية حالياً في معالجة طلبك، يرجى المحاولة لاحقاً."

def generate_service_description(title):
    try:
        api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
        if not api_key:
            return "Error: GEMINI_API_KEY not configured."

        client = genai.Client(api_key=api_key)

        prompt = f"""
أنت خبير مبيعات محترف وكوبي رايتر (Copywriter) على منصة عمل حر (Freelance Marketplace).
كتب المستقل هذا العنوان لخدمته: '{title}'.
مهمتك: كتابة وصف تسويقي وإقناعي جاهز لهذه الخدمة، باللغة العربية الواضحة والاحترافية.

يجب أن يحتوي الوصف على الهيكل التالي فقط بدون أي مقدمات أو تحيات:
1. مقدمة تشويقية وجذابة (سطرين كحد أقصى) تبرز أهمية الخدمة للعميل.
2. "ماذا سأقدم لك؟" (في شكل نقاط واضحة ومغرية).
3. "لماذا تختارني؟" (في شكل نقاط تبرز الاحترافية، الجودة، وسرعة التسليم).

استخدم الإيموجي المناسبة بشكل غير مبالغ فيه ولا تستخدم أكواد برمجية.
عدم إعطاء أي توجيهات للمستقل، فقط النص التسويقي الجاهز للاستخدام مباشرة في الموقع.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if response and response.text:
            return response.text
        else:
            return ""

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ""
