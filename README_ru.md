# TrendGenBot

[\[📂 GitHub репозиторий модели\]](https://github.com/H1merka/InternVL2_5-4B-QLoRA-LLM-RussianSummarization)  [\[🤗 HF репозиторий модели\]](https://huggingface.co/H1merka/InternVL2_5-4B-QLoRA-LLM-RussianSummarization) [\[📂 GitHub репозиторий приложения\]](https://github.com/H1merka/TrendGenBot) [\[VK группа с чат-ботом\]](https://vk.com/club230649268)

## Введение

ВК чат-бот для генерации рекомендаций по контенту для сообществ ВК с применением ИИ-агента


## Описание


ИИ-агент подключается через чат-бота к группе ВКонтакте для генерации рекомендаций по контент-плану на основе статистики и содержания постов.

Чат-бот использует [InternVL2_5-4B](https://huggingface.co/OpenGVLab/InternVL2_5-4B) модель с LoRA [адаптером](https://huggingface.co/H1merka/InternVL2_5-4B-QLoRA-LLM-RussianSummarization) для суммаризации и генерации

[Ключ доступа пользователя](https://dev.vk.com/ru/api/access-token/authcode-flow-user) и [ключ доступа сообщества](https://dev.vk.com/ru/api/access-token/community-token/in-community-settings) необходимы для корректной работы приложения

Частично реализована VK ID авторизация с PKCE flow

## Лицензия

Этот проект выпущен под лицензией MIT. В этом проекте используется предварительно обученная модель InternVL2_5-4B, которая лицензирована под MIT.

## Команда разработчиков
GitHub: [https://github.com/H1merka](https://github.com/H1merka)

## Цитирование

Если вы сочтете этот проект полезным, пожалуйста, рассмотрите возможность цитирования:

```BibTeX
@article{chen2024expanding,
  title={Expanding Performance Boundaries of Open-Source Multimodal Models with Model, Data, and Test-Time Scaling},
  author={Chen, Zhe and Wang, Weiyun and Cao, Yue and Liu, Yangzhou and Gao, Zhangwei and Cui, Erfei and Zhu, Jinguo and Ye, Shenglong and Tian, Hao and Liu, Zhaoyang and others},
  journal={arXiv preprint arXiv:2412.05271},
  year={2024}
}
@article{gao2024mini,
  title={Mini-internvl: A flexible-transfer pocket multimodal model with 5\% parameters and 90\% performance},
  author={Gao, Zhangwei and Chen, Zhe and Cui, Erfei and Ren, Yiming and Wang, Weiyun and Zhu, Jinguo and Tian, Hao and Ye, Shenglong and He, Junjun and Zhu, Xizhou and others},
  journal={arXiv preprint arXiv:2410.16261},
  year={2024}
}
@article{chen2024far,
  title={How Far Are We to GPT-4V? Closing the Gap to Commercial Multimodal Models with Open-Source Suites},
  author={Chen, Zhe and Wang, Weiyun and Tian, Hao and Ye, Shenglong and Gao, Zhangwei and Cui, Erfei and Tong, Wenwen and Hu, Kongzhi and Luo, Jiapeng and Ma, Zheng and others},
  journal={arXiv preprint arXiv:2404.16821},
  year={2024}
}
@inproceedings{chen2024internvl,
  title={Internvl: Scaling up vision foundation models and aligning for generic visual-linguistic tasks},
  author={Chen, Zhe and Wu, Jiannan and Wang, Wenhai and Su, Weijie and Chen, Guo and Xing, Sen and Zhong, Muyan and Zhang, Qinglong and Zhu, Xizhou and Lu, Lewei and others},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={24185--24198},
  year={2024}
}
```
