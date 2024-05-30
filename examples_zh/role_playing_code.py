# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
from colorama import Fore

from camel.configs import ChatGPTConfig, OpenSourceConfig
from camel.societies import RolePlaying
from camel.types import ModelType, TaskType
from camel.utils import print_text_animated


def main(model_type=None, chat_turn_limit=50, model_path=" ",
         server_url=" ") -> None:
    task_prompt = "开发一个投票应用程序"
    language = "JavaScript"
    domain = "社会学"
    meta_dict = {"language": language, "domain": domain}

    agent_kwargs = {
        role: dict(
            model_type=model_type,
            model_config=OpenSourceConfig(
                model_path=model_path,
                server_url=server_url,
                api_params=ChatGPTConfig(temperature=0.5, frequency_penalty=0.3),
            ),
        )
        for role in ["assistant", "user", "task-specify"]
    }

    role_play_session = RolePlaying(
        assistant_role_name=f"{language}程序员",
        assistant_agent_kwargs=agent_kwargs["assistant"],
        user_role_name=f"{domain}领域的工作者",
        user_agent_kwargs=agent_kwargs["user"],
        task_prompt=task_prompt,
        with_task_specify=True,
        task_specify_agent_kwargs=agent_kwargs["task-specify"],
        task_type=TaskType.CODE,
        extend_sys_msg_meta_dicts=[meta_dict, meta_dict],
        extend_task_specify_meta_dict=meta_dict,
    )

    print(
        Fore.GREEN +
        f"AI Assistant sys message:\n{role_play_session.assistant_sys_msg}\n")
    print(Fore.BLUE +
          f"AI User sys message:\n{role_play_session.user_sys_msg}\n")

    print(Fore.YELLOW + f"Original task prompt:\n{task_prompt}\n")
    print(
        Fore.CYAN +
        f"Specified task prompt:\n{role_play_session.specified_task_prompt}\n")
    print(Fore.RED + f"Final task prompt:\n{role_play_session.task_prompt}\n")

    n = 0
    input_assistant_msg = role_play_session.init_chat()
    while n < chat_turn_limit:
        n += 1
        assistant_response, user_response = role_play_session.step(
            input_assistant_msg)

        if assistant_response.terminated:
            print(Fore.GREEN +
                  ("AI Assistant terminated. Reason: "
                   f"{assistant_response.info['termination_reasons']}."))
            break
        if user_response.terminated:
            print(Fore.GREEN +
                  ("AI User terminated. "
                   f"Reason: {user_response.info['termination_reasons']}."))
            break

        print_text_animated(Fore.BLUE +
                            f"AI User:\n\n{user_response.msg.content}\n")
        print_text_animated(Fore.GREEN + "AI Assistant:\n\n"
                            f"{assistant_response.msg.content}\n")

        if "任务完成" in user_response.msg.content:
            break

        input_assistant_msg = assistant_response.msg


if __name__ == "__main__":
    # Here :obj:`model_type` can be any of the supported open-source
    # model types and :obj:`model_path` should be set corresponding to
    # model type. For example, to use Vicuna, we can set:
    # model_path = "lmsys/vicuna-7b-v1.5"
    main(
        model_type=ModelType.QWEN,
        model_path="../lm_model/Qwen1.5-7B-Chat",
        server_url="http://localhost:8000/v1",
    )
