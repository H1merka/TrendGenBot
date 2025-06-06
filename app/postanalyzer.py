from transformers import AutoModel, AutoTokenizer
import torch
from torchvision import transforms as T
from torchvision.transforms.functional import InterpolationMode
from PIL import Image
from config import MODEL_NAME, IMAGENET_MEAN, IMAGENET_STD


class PostAnalyzer:
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        image_size: int = 448,
        max_new_tokens: int = 128,
        torch_dtype=torch.float16,
    ):
        self.image_size = image_size
        self.torch_dtype = torch_dtype
        self.max_new_tokens = max_new_tokens

        # Tokenizer uploading
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True
        )

        # Model uploading
        self.model = AutoModel.from_pretrained(
            model_name,
            device_map={"": "cpu"},
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        ).eval()

        # Preparing image transformation pipeline
        self.transform = T.Compose([
            T.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Image preprocessing function"""
        image = image.convert('RGB')
        tensor = self.transform(image).unsqueeze(0)
        return tensor.to(dtype=self.torch_dtype, device=self.model.device)

    def analyze_posts(self, posts: list[tuple[Image.Image | None, str | None]]) -> str:
        generation_config = dict(max_new_tokens=self.max_new_tokens, do_sample=False)
        responses = []

        for image, additional_text in posts:
            # Checking the availability of data
            if image is None and (additional_text is None or additional_text.strip() == ""):
                continue

            pixel_values = None
            question_parts = []

            if image is not None:
                pixel_values = self.preprocess_image(image)
                question_parts.append("<image>")

            if additional_text is not None and additional_text.strip() != "":
                question_parts.append(f"Текст: '{additional_text}'")

            # Forming a question depending on the availability of data
            if len(question_parts) == 2:
                question = (
                    f"{question_parts[0]}\n"
                    "Определи тему, объединяющую визуальное "
                    "содержание изображения и следующий текст: "
                    f"{question_parts[1]}"
                )
            elif len(question_parts) == 1:
                if pixel_values is not None:
                    question = (
                        f"{question_parts[0]}\n"
                        "Определи тему визуального содержания изображения."
                    )
                else:
                    question = (
                        f"Определи тему следующего текста: {question_parts[0]}"
                    )

            response = self.model.chat(
                self.tokenizer, pixel_values, question, generation_config
            )
            responses.append(response)

        result = "\n".join(responses)

        return result
