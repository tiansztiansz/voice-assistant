from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

device = torch.device("cuda")
tokenizer = T5Tokenizer.from_pretrained("ClueAI/ChatYuan-large-v2")
model = (
    T5ForConditionalGeneration.from_pretrained("ClueAI/ChatYuan-large-v2")
    .half()
    .to(device)
)


def preprocess(text):
    text = text.replace("\n", "\\n").replace("\t", "\\t")
    return text


def postprocess(text):
    return text.replace("\\n", "\n").replace("\\t", "\t").replace("%20", "  ")


def answer(text, sample=True, top_p=0.9, temperature=0.7, context=""):
    """sample：是否抽样。生成任务，可以设置为True;
    top_p：0-1之间，生成的内容越多样"""
    text = f"{context}\n用户：{text}\n小元："
    text = text.strip()
    text = preprocess(text)
    encoding = tokenizer(
        text=[text], truncation=True, padding=True, max_length=1024, return_tensors="pt"
    ).to(device)
    if not sample:
        out = model.generate(
            **encoding,
            return_dict_in_generate=True,
            output_scores=False,
            max_new_tokens=1024,
            num_beams=1,
            length_penalty=0.6,
        )
    else:
        out = model.generate(
            **encoding,
            return_dict_in_generate=True,
            output_scores=False,
            max_new_tokens=1024,
            do_sample=True,
            top_p=top_p,
            temperature=temperature,
            no_repeat_ngram_size=12,
        )
    out_text = tokenizer.batch_decode(out["sequences"], skip_special_tokens=True)
    return postprocess(out_text[0])


class ChatYuan:
    def __init__(self) -> None:
        pass

    def text2text(input_text):
        output_text = answer(input_text)
        return output_text


if __name__ == "__main__":
    text2text = ChatYuan.text2text("世界的意义")
    print(text2text)
