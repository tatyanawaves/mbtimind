"""MBTI Question Bank.

Contains 60+ forced-choice questions across 4 scales + L-scale items.
Each question presents two options; one maps to each pole of the scale.

For MVP: hardcoded questions in Russian.
Future: load from DB, support KZ/EN, adaptive ordering.
"""
import uuid

# Generate stable UUIDs from index for reproducibility
def _qid(index: int) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"mbti-question-{index}"))


# Question bank: 60 MBTI questions (15 per scale) + 8 L-scale questions = 68 total
QUESTIONS = [
    # === E/I Scale (15 questions) ===
    {
        "id": _qid(1), "order_index": 1, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "В свободное время вы предпочитаете:",
        "option_a_ru": "Встречаться с друзьями, ходить на мероприятия",
        "option_b_ru": "Проводить время в одиночестве или с одним близким человеком",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(2), "order_index": 2, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "После долгого рабочего дня вы восстанавливаете энергию:",
        "option_a_ru": "Общаясь с людьми, обсуждая события дня",
        "option_b_ru": "В тишине и уединении",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(3), "order_index": 3, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "На вечеринке вы обычно:",
        "option_a_ru": "Знакомитесь с новыми людьми, легко вступаете в разговор",
        "option_b_ru": "Общаетесь с теми, кого уже знаете",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(4), "order_index": 4, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "При решении проблемы вы предпочитаете:",
        "option_a_ru": "Обсудить её с другими, проговорить вслух",
        "option_b_ru": "Обдумать всё самостоятельно, прежде чем обсуждать",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(5), "order_index": 5, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "Вам комфортнее работать:",
        "option_a_ru": "В открытом пространстве, среди коллег",
        "option_b_ru": "В отдельном кабинете или удалённо",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(6), "order_index": 6, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "Вы считаете себя:",
        "option_a_ru": "Общительным человеком, которому легко даются контакты",
        "option_b_ru": "Сдержанным человеком, который ценит глубину отношений",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(7), "order_index": 7, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "На совещании вы чаще:",
        "option_a_ru": "Высказываетесь первым, делитесь идеями сразу",
        "option_b_ru": "Слушаете других и формулируете мнение внутренне",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(8), "order_index": 8, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "Ваш идеальный выходной:",
        "option_a_ru": "Активный день с друзьями, события, движение",
        "option_b_ru": "Спокойный день с книгой, хобби или прогулкой",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(9), "order_index": 9, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "Когда вам нужна поддержка, вы:",
        "option_a_ru": "Звоните друзьям, ищете общения",
        "option_b_ru": "Переживаете внутри, разбираетесь сами",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(10), "order_index": 10, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "Вы предпочитаете учиться:",
        "option_a_ru": "В группе, через обсуждение и взаимодействие",
        "option_b_ru": "Самостоятельно, в своём темпе",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(11), "order_index": 11, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "У вас много знакомых?",
        "option_a_ru": "Да, у меня широкий круг общения",
        "option_b_ru": "Нет, у меня несколько близких друзей",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(12), "order_index": 12, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "Телефонный звонок от незнакомого номера:",
        "option_a_ru": "Отвечаю без раздумий",
        "option_b_ru": "Предпочитаю не отвечать, перезвоню если нужно",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(13), "order_index": 13, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "Долгая тишина в компании вас:",
        "option_a_ru": "Напрягает, хочется заполнить разговором",
        "option_b_ru": "Не беспокоит, молчание бывает комфортным",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(14), "order_index": 14, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "Вы лучше усваиваете информацию когда:",
        "option_a_ru": "Объясняете её кому-то другому",
        "option_b_ru": "Записываете и перечитываете самостоятельно",
        "option_a_direction": "E", "option_b_direction": "I",
    },
    {
        "id": _qid(15), "order_index": 15, "scale": "E/I", "question_type": "forced_choice",
        "text_ru": "В новом коллективе вы:",
        "option_a_ru": "Быстро адаптируетесь и заводите контакты",
        "option_b_ru": "Наблюдаете со стороны, осторожно сближаетесь",
        "option_a_direction": "E", "option_b_direction": "I",
    },

    # === S/N Scale (15 questions) ===
    {
        "id": _qid(16), "order_index": 16, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "При изучении нового вы фокусируетесь на:",
        "option_a_ru": "Конкретных фактах и деталях",
        "option_b_ru": "Общей картине и взаимосвязях",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(17), "order_index": 17, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Вы больше доверяете:",
        "option_a_ru": "Собственному опыту и проверенным методам",
        "option_b_ru": "Интуиции и предчувствиям",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(18), "order_index": 18, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Вас больше привлекает:",
        "option_a_ru": "Практическое применение идеи здесь и сейчас",
        "option_b_ru": "Теоретические возможности и потенциал идеи",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(19), "order_index": 19, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Описывая событие, вы чаще:",
        "option_a_ru": "Рассказываете последовательно, с деталями",
        "option_b_ru": "Передаёте общее впечатление и смысл",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(20), "order_index": 20, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "В работе вам важнее:",
        "option_a_ru": "Чёткие инструкции и понятные шаги",
        "option_b_ru": "Свобода действий и возможность импровизировать",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(21), "order_index": 21, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Вы предпочитаете задачи, которые:",
        "option_a_ru": "Имеют конкретный, измеримый результат",
        "option_b_ru": "Требуют креативного, нестандартного подхода",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(22), "order_index": 22, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Читая книгу, вы обращаете внимание на:",
        "option_a_ru": "Конкретные описания, факты, хронологию",
        "option_b_ru": "Символы, метафоры, скрытые смыслы",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(23), "order_index": 23, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Вам ближе утверждение:",
        "option_a_ru": "Я реалист, вижу вещи такими, какие они есть",
        "option_b_ru": "Я мечтатель, вижу вещи такими, какими они могут стать",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(24), "order_index": 24, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "При покупке техники вы:",
        "option_a_ru": "Изучаете характеристики, сравниваете параметры",
        "option_b_ru": "Оцениваете общее впечатление, дизайн, ощущение",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(25), "order_index": 25, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Вы скорее скажете:",
        "option_a_ru": "Давайте разберёмся в деталях",
        "option_b_ru": "Давайте посмотрим на это шире",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(26), "order_index": 26, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Планируя отпуск, вы:",
        "option_a_ru": "Составляете подробный план по дням",
        "option_b_ru": "Определяете общее направление и действуете по ситуации",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(27), "order_index": 27, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Вас раздражает когда:",
        "option_a_ru": "Говорят абстрактно, без конкретики",
        "option_b_ru": "Завязли в деталях, упуская суть",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(28), "order_index": 28, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "В школе/университете вам давались лучше:",
        "option_a_ru": "Точные науки с конкретными ответами",
        "option_b_ru": "Гуманитарные предметы с множеством интерпретаций",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(29), "order_index": 29, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Вы лучше запоминаете:",
        "option_a_ru": "Факты, даты, конкретные события",
        "option_b_ru": "Впечатления, идеи, концепции",
        "option_a_direction": "S", "option_b_direction": "N",
    },
    {
        "id": _qid(30), "order_index": 30, "scale": "S/N", "question_type": "forced_choice",
        "text_ru": "Вам интереснее думать о:",
        "option_a_ru": "Настоящем — что происходит сейчас",
        "option_b_ru": "Будущем — что может произойти",
        "option_a_direction": "S", "option_b_direction": "N",
    },

    # === T/F Scale (15 questions) ===
    {
        "id": _qid(31), "order_index": 31, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Принимая решение, вы опираетесь на:",
        "option_a_ru": "Логику, объективные факты и анализ",
        "option_b_ru": "Чувства, ценности и влияние на людей",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(32), "order_index": 32, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "В споре для вас важнее:",
        "option_a_ru": "Быть правым, найти истину",
        "option_b_ru": "Сохранить хорошие отношения",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(33), "order_index": 33, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Критикуя чью-то работу, вы:",
        "option_a_ru": "Говорите прямо, что не так, и что исправить",
        "option_b_ru": "Стараетесь смягчить, учитываете чувства человека",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(34), "order_index": 34, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Вас больше расстроит если вас назовут:",
        "option_a_ru": "Нелогичным",
        "option_b_ru": "Бесчувственным",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(35), "order_index": 35, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Руководитель должен быть прежде всего:",
        "option_a_ru": "Справедливым и последовательным",
        "option_b_ru": "Отзывчивым и понимающим",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(36), "order_index": 36, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "При увольнении сотрудника вы бы:",
        "option_a_ru": "Приняли решение на основе показателей эффективности",
        "option_b_ru": "Учли бы личные обстоятельства человека",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(37), "order_index": 37, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Вам ближе комплимент:",
        "option_a_ru": "Ты очень умный и компетентный",
        "option_b_ru": "Ты очень добрый и чуткий",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(38), "order_index": 38, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Когда друг рассказывает о проблеме, вы:",
        "option_a_ru": "Предлагаете решение или совет",
        "option_b_ru": "Выслушиваете и сочувствуете",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(39), "order_index": 39, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "В команде вы цените:",
        "option_a_ru": "Компетентность и результативность",
        "option_b_ru": "Взаимоподдержку и дружескую атмосферу",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(40), "order_index": 40, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Вы скорее согласитесь, что:",
        "option_a_ru": "Законы должны быть одинаковы для всех без исключений",
        "option_b_ru": "Каждый случай уникален и заслуживает индивидуального подхода",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(41), "order_index": 41, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Фильмы, которые вам нравятся, чаще:",
        "option_a_ru": "Интеллектуально интересны, с хорошей логикой сюжета",
        "option_b_ru": "Эмоционально сильные, трогают до глубины души",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(42), "order_index": 42, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Получив плохую оценку или отзыв, вы:",
        "option_a_ru": "Анализируете, что можно улучшить",
        "option_b_ru": "Переживаете, чувствуете себя задетым",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(43), "order_index": 43, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Справедливость для вас это:",
        "option_a_ru": "Равные правила и последовательность",
        "option_b_ru": "Учёт обстоятельств и милосердие",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(44), "order_index": 44, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Вы считаете что лучший аргумент:",
        "option_a_ru": "Построен на фактах и доказательствах",
        "option_b_ru": "Учитывает чувства и потребности всех сторон",
        "option_a_direction": "T", "option_b_direction": "F",
    },
    {
        "id": _qid(45), "order_index": 45, "scale": "T/F", "question_type": "forced_choice",
        "text_ru": "Люди иногда говорят что вы:",
        "option_a_ru": "Слишком критичны или прямолинейны",
        "option_b_ru": "Слишком мягки или принимаете всё близко к сердцу",
        "option_a_direction": "T", "option_b_direction": "F",
    },

    # === J/P Scale (15 questions) ===
    {
        "id": _qid(46), "order_index": 46, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Вы предпочитаете:",
        "option_a_ru": "Планировать заранее и следовать плану",
        "option_b_ru": "Действовать гибко, адаптируясь к ситуации",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(47), "order_index": 47, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Дедлайны для вас:",
        "option_a_ru": "Помогают организоваться, вы завершаете заранее",
        "option_b_ru": "Создают давление, вы работаете продуктивнее в последний момент",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(48), "order_index": 48, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Ваш рабочий стол обычно:",
        "option_a_ru": "В порядке, всё на своих местах",
        "option_b_ru": "В творческом беспорядке, но вы знаете где что",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(49), "order_index": 49, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Когда планы неожиданно меняются, вы:",
        "option_a_ru": "Раздражаетесь, сложно перестроиться",
        "option_b_ru": "Легко адаптируетесь, видите новые возможности",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(50), "order_index": 50, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Вы предпочитаете:",
        "option_a_ru": "Завершить одно дело, прежде чем браться за другое",
        "option_b_ru": "Вести несколько проектов параллельно",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(51), "order_index": 51, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Принимая решение, вы:",
        "option_a_ru": "Стараетесь определиться как можно скорее",
        "option_b_ru": "Оставляете опции открытыми как можно дольше",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(52), "order_index": 52, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Списки дел (to-do) для вас:",
        "option_a_ru": "Необходимый инструмент, ведёте постоянно",
        "option_b_ru": "Пишете иногда, но редко следуете им строго",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(53), "order_index": 53, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "В путешествии вам важнее:",
        "option_a_ru": "Иметь забронированный маршрут и расписание",
        "option_b_ru": "Свобода менять планы на ходу",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(54), "order_index": 54, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Вам легче работать когда:",
        "option_a_ru": "Есть чёткая структура и правила",
        "option_b_ru": "Есть свобода и минимум ограничений",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(55), "order_index": 55, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Незавершённые дела вас:",
        "option_a_ru": "Беспокоят, хочется довести до конца",
        "option_b_ru": "Не сильно тревожат, можно вернуться позже",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(56), "order_index": 56, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Вы чаще приходите на встречи:",
        "option_a_ru": "Вовремя или заранее",
        "option_b_ru": "В последний момент или чуть опаздываете",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(57), "order_index": 57, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Перед важным событием вы:",
        "option_a_ru": "Готовитесь заранее, составляете план",
        "option_b_ru": "Полагаетесь на импровизацию и вдохновение момента",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(58), "order_index": 58, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Правила для вас:",
        "option_a_ru": "Полезны и помогают всем жить лучше",
        "option_b_ru": "Иногда мешают и не учитывают контекст",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(59), "order_index": 59, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Вы скорее:",
        "option_a_ru": "Начинаете работу пораньше, чтобы не торопиться",
        "option_b_ru": "Откладываете до последнего, но выполняете в срок",
        "option_a_direction": "J", "option_b_direction": "P",
    },
    {
        "id": _qid(60), "order_index": 60, "scale": "J/P", "question_type": "forced_choice",
        "text_ru": "Вечер пятницы — вы предпочитаете:",
        "option_a_ru": "Знать заранее, чем будете заниматься",
        "option_b_ru": "Посмотреть по настроению, решить спонтанно",
        "option_a_direction": "J", "option_b_direction": "P",
    },

    # === L-Scale (8 questions) — social desirability detection ===
    {
        "id": _qid(61), "order_index": 61, "scale": None, "question_type": "l_scale",
        "text_ru": "Бывает ли, что вы опаздываете?",
        "option_a_ru": "Да, иногда опаздываю",  # Honest
        "option_b_ru": "Нет, я никогда не опаздываю",  # Socially desirable (suspicious)
        "option_a_direction": None, "option_b_direction": None,
    },
    {
        "id": _qid(62), "order_index": 62, "scale": None, "question_type": "l_scale",
        "text_ru": "Всегда ли вы выполняете свои обещания?",
        "option_a_ru": "Стараюсь, но иногда не получается",
        "option_b_ru": "Да, всегда без исключений",
        "option_a_direction": None, "option_b_direction": None,
    },
    {
        "id": _qid(63), "order_index": 63, "scale": None, "question_type": "l_scale",
        "text_ru": "Случалось ли вам говорить неправду?",
        "option_a_ru": "Да, в жизни бывало",
        "option_b_ru": "Нет, я всегда говорю только правду",
        "option_a_direction": None, "option_b_direction": None,
    },
    {
        "id": _qid(64), "order_index": 64, "scale": None, "question_type": "l_scale",
        "text_ru": "Бывает ли что вы раздражаетесь на людей?",
        "option_a_ru": "Да, это нормально",
        "option_b_ru": "Нет, я никогда не раздражаюсь",
        "option_a_direction": None, "option_b_direction": None,
    },
    {
        "id": _qid(65), "order_index": 65, "scale": None, "question_type": "l_scale",
        "text_ru": "Всегда ли вы доводите начатое до конца?",
        "option_a_ru": "Не всегда, зависит от ситуации",
        "option_b_ru": "Да, абсолютно всегда",
        "option_a_direction": None, "option_b_direction": None,
    },
    {
        "id": _qid(66), "order_index": 66, "scale": None, "question_type": "l_scale",
        "text_ru": "Бывает ли что вы сплетничаете?",
        "option_a_ru": "Иногда обсуждаю других, это человечно",
        "option_b_ru": "Нет, я никогда не обсуждаю людей за их спиной",
        "option_a_direction": None, "option_b_direction": None,
    },
    {
        "id": _qid(67), "order_index": 67, "scale": None, "question_type": "l_scale",
        "text_ru": "Случалось ли вам чувствовать зависть?",
        "option_a_ru": "Да, это нормальное чувство",
        "option_b_ru": "Нет, я никогда не завидую",
        "option_a_direction": None, "option_b_direction": None,
    },
    {
        "id": _qid(68), "order_index": 68, "scale": None, "question_type": "l_scale",
        "text_ru": "Все ли ваши привычки хорошие?",
        "option_a_ru": "Нет, есть и плохие привычки",
        "option_b_ru": "Да, у меня только хорошие привычки",
        "option_a_direction": None, "option_b_direction": None,
    },
]


def get_questions_for_attempt(start_index: int, count: int) -> list[dict]:
    """Get a batch of questions starting from index."""
    # For MVP: serve questions in order. Future: randomize per attempt.
    end_index = min(start_index + count, len(QUESTIONS))
    questions = QUESTIONS[start_index:end_index]

    # Return only participant-facing fields
    return [
        {
            "id": q["id"],
            "text_ru": q["text_ru"],
            "option_a_ru": q["option_a_ru"],
            "option_b_ru": q["option_b_ru"],
            "index": q["order_index"],
        }
        for q in questions
    ]


def get_all_questions_map() -> dict[str, dict]:
    """Get all questions as a lookup map by ID (for scoring)."""
    return {q["id"]: q for q in QUESTIONS}
