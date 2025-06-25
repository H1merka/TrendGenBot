from transformers import AutoModel, AutoTokenizer
import torch
from torchvision import transforms as T
from torchvision.transforms.functional import InterpolationMode
from PIL import Image
from config import MODEL_NAME, IMAGENET_MEAN, IMAGENET_STD
from typing import Optional


class PostAnalyzer:
    """
    A class that analyzes VK posts using a vision-language model.
    It supports multimodal input (images and text) and returns topic-based recommendations.
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        image_size: int = 448,
        max_new_tokens: int = 128,
        torch_dtype: torch.dtype = torch.float16,
    ):
        """
        Initializes the analyzer with model, tokenizer, and preprocessing pipeline.

        Args:
            model_name (str): Name or path of the pretrained model.
            image_size (int): Target size for image preprocessing.
            max_new_tokens (int): Max tokens to generate in the response.
            torch_dtype (torch.dtype): Precision to load the model with.
        """
        self.image_size = image_size
        self.torch_dtype = torch_dtype
        self.max_new_tokens = max_new_tokens

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True
        )

        # Load model
        self.model = AutoModel.from_pretrained(
            model_name,
            device_map={"": "cpu"},  # Set to "cpu" or update for GPU inference
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        ).eval()

        # Define image preprocessing pipeline
        self.transform = T.Compose([
            T.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocess a PIL image into a normalized tensor suitable for model input.

        Args:
            image (Image.Image): Input image.

        Returns:
            torch.Tensor: Preprocessed image tensor (1 x C x H x W).
        """
        image = image.convert('RGB')
        tensor = self.transform(image).unsqueeze(0)
        return tensor.to(dtype=self.torch_dtype, device=self.model.device)

    def analyze_posts(
        self,
        posts: list[tuple[Optional[Image.Image], Optional[str]]]
    ) -> str:
        """
        Analyze a list of (image, text) post pairs and generate content suggestions.

        Args:
            posts (list): List of tuples containing (Image or None, text or None).

        Returns:
            str: Combined model-generated responses for all valid posts.
        """
        generation_config = {
            "max_new_tokens": self.max_new_tokens,
            "do_sample": False
        }
        responses: list[str] = []

        for image, additional_text in posts:
            # Skip if both image and text are missing or empty
            if image is None and (additional_text is None or additional_text.strip() == ""):
                continue

            pixel_values: Optional[torch.Tensor] = None
            question_parts: list[str] = []

            if image is not None:
                pixel_values = self.preprocess_image(image)
                question_parts.append("<image>")

            if additional_text and additional_text.strip():
                question_parts.append(f"Текст: '{additional_text}'")

            # Build the prompt depending on available data
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

            # Generate model response
            response: str = self.model.chat(
                self.tokenizer, pixel_values, question, generation_config
            )
            responses.append(response)

        # Join all responses into a final summary
        result: str = "\n".join(responses)
        return result
