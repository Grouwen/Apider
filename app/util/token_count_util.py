def count_message_tokens(messages: list[dict]) -> int:
    """
    粗略估算 messages 列表的 token 用量
    适用于 GPT/Qwen 等主流 LLM，误差范围 ±15%
    """
    total = 0

    for msg in messages:
        # 1. 每条消息的固定结构开销 (role, separator 等)
        total += 4

        # 2. 文本内容估算
        content = msg.get('content', '') or ''
        if isinstance(content, dict):
            # 多模态/结构化 content，转为字符串估算
            content = str(content)

        cn_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
        other_chars = len(content) - cn_chars

        # 中文 ~1.5字符/token, 英文/代码 ~4字符/token
        total += int(cn_chars / 1.5) + int(other_chars / 4)

        # 3. tool_calls 结构化开销
        tool_calls = msg.get('tool_calls')
        if tool_calls:
            for tc in tool_calls:
                total += 4  # 每个 tool_call 的结构开销
                # function name
                fname = tc.get('function', {}).get('name', '')
                total += max(1, len(fname) // 4)
                # arguments (通常是 JSON 字符串)
                args = tc.get('function', {}).get('arguments', '')
                if isinstance(args, str):
                    total += max(1, len(args) // 4)
                else:
                    total += max(1, len(str(args)) // 4)

        # 4. tool_call_id (assistant 回复中引用 / tool 角色中携带)
        tcid = msg.get('tool_call_id', '')
        if tcid:
            total += max(1, len(tcid) // 4)

        # 5. role 本身
        total += max(1, len(msg.get('role', '')) // 4)

    # 6. 全局 reply 前缀开销 (priming tokens)
    total += 2

    return total