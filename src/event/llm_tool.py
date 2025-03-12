import json

from astrbot.api.event import AstrMessageEvent

DEFALT_PROMPT = ("刚才我通过调用工具{}获得了一份结果,现在需要整理语言返回给用户。"
                 "结果使用<result>标签包裹\n"
                 "<result>\n{}\n</result>")

async def return_tool_result_with_llm(plugin_obj,
                                      event: AstrMessageEvent,
                                      tool_result: str,
                                      prompt: str = DEFALT_PROMPT):
    func_tools_mgr = plugin_obj.context.get_llm_tool_manager()
    # input_context = {'role': 'user',
    #                  'content': tool_result}
    # 获取用户当前与 LLM 的对话以获得上下文信息。
    curr_cid = await plugin_obj.context.conversation_manager.get_curr_conversation_id(
        event.unified_msg_origin)  # 当前用户所处对话的对话id，是一个 uuid。
    conversation = None  # 对话对象
    context = []  # 上下文列表
    if curr_cid:
        conversation = await plugin_obj.context.conversation_manager.get_conversation(event.unified_msg_origin, curr_cid)
        context = json.loads(conversation.history)
    # 可以用这个方法自行为用户新建一个对话
    # curr_cid = await self.context.conversation_manager.new_conversation(event.unified_msg_origin)

    # 方法1. 最底层的调用 LLM 的方式, 如果启用了函数调用，不会进行产生任何副作用（不会调用函数工具,进行对话管理等），只是会回传所调用的函数名和参数
    llm = plugin_obj.context.get_provider_by_id('deepseek_v3')
    llm_response = await llm.text_chat(
        prompt=DEFALT_PROMPT.format('return_tool_result_with_llm', tool_result),
        session_id=None,  # 此已经被废弃
        contexts=context,  # 也可以用上面获得的用户当前的对话记录 context
        image_urls=[],  # 图片链接，支持路径和网络链接
        func_tool=None,  # 当前用户启用的函数调用工具。如果不需要，可以不传
        system_prompt=""  # 系统提示，可以不传
    )
    # contexts 是历史记录。格式与 OpenAI 的上下文格式格式一致。即使用户正在使用 gemini，也会自动转换为 OpenAI 的上下文格式
    # contexts = [
    #     { "role": "system", "content": "你是一个助手。"},
    #     { "role": "user", "content": "你好"}
    # ]
    # text_chat() 将会将 contexts 和 prompt,image_urls 合并起来形成一个上下文，然后调用 LLM 进行对话
    if llm_response.role == "assistant":
        return event.plain_result(llm_response.completion_text)  # 回复的文本
    else:
        return event.plain_result(f'return role wrong: {llm_response.role}')

async def return_evebot_result(plugin_obj,
                              event: AstrMessageEvent,
                              question_str: str,
                              prompt: str = DEFALT_PROMPT):
    curr_cid = await plugin_obj.context.conversation_manager.get_curr_conversation_id(
        event.unified_msg_origin)  # 当前用户所处对话的对话id，是一个 uuid。
    conversation = None  # 对话对象
    context = []  # 上下文列表
    if curr_cid:
        conversation = await plugin_obj.context.conversation_manager.get_conversation(event.unified_msg_origin, curr_cid)
        context = json.loads(conversation.history)
    # 可以用这个方法自行为用户新建一个对话
    # curr_cid = await self.context.conversation_manager.new_conversation(event.unified_msg_origin)

    # 方法1. 最底层的调用 LLM 的方式, 如果启用了函数调用，不会进行产生任何副作用（不会调用函数工具,进行对话管理等），只是会回传所调用的函数名和参数
    llm = plugin_obj.context.get_provider_by_id('eve_bot')
    llm_response = await llm.text_chat(
        prompt=question_str,
        session_id=event.unified_msg_origin,  # 此已经被废弃
        contexts=context,  # 也可以用上面获得的用户当前的对话记录 context
        image_urls=[],  # 图片链接，支持路径和网络链接
        func_tool=None,  # 当前用户启用的函数调用工具。如果不需要，可以不传
        system_prompt=""  # 系统提示，可以不传
    )

    if llm_response.role == "assistant":
        context.append({"role": "user", "content": llm_response.completion_text})
        return event.request_llm(
            prompt="你因为无法回答eve相关的问题所以问了eveonline知识库问答机器人，你称呼她为喜欢玩eve的小卡。\n"
                   "现在你需要根据喜欢玩eve的小卡的回答组织回复。",
            func_tool_manager=None,
            session_id=curr_cid, # 对话id。如果指定了对话id，将会记录对话到数据库
            contexts=context, # 列表。如果不为空，将会使用此上下文与 LLM 对话。
            system_prompt="",
            image_urls=[], # 图片链接，支持路径和网络链接
            conversation=conversation # 如果指定了对话，将会记录对话
        )
    else:
        return event.plain_result(f'return role wrong: {llm_response.role}')

