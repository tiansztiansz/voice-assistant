import paddle
from paddlenlp.transformers import T5Tokenizer, T5ForConditionalGeneration
from paddlenlp.transformers import AutoTokenizer, T5ForConditionalGeneration


tokenizer = AutoTokenizer.from_pretrained("ClueAI/ChatYuan-large-v1", from_hf_hub=False)
model = T5ForConditionalGeneration.from_pretrained(
    "ClueAI/ChatYuan-large-v1", from_hf_hub=False
)


model.eval()


def preprocess(text):
    text = text.replace("\n", "\\n").replace("\t", "\\t")
    return text


def postprocess(text):
    return text.replace("\\n", "\n").replace("\\t", "\t")


def answer(text, sample=True, top_p=1, temperature=0.7):
    """sample：是否抽样。生成任务，可以设置为True;
    top_p：0-1之间，生成的内容越多样"""
    text = preprocess(text)
    encoding = tokenizer(
        text=[text], truncation=True, padding=True, max_length=768, return_tensors="pd"
    )
    if not sample:
        out = model.generate(
            **encoding,
            return_dict_in_generate=True,
            output_scores=False,
            max_length=512,
            max_new_tokens=512,
            num_beams=1,
            length_penalty=0.4,
        )
    else:
        out = model.generate(
            **encoding,
            return_dict_in_generate=True,
            output_scores=False,
            max_length=512,
            max_new_tokens=512,
            do_sample=True,
            top_p=top_p,
            temperature=temperature,
            no_repeat_ngram_size=3,
        )

    out_text = tokenizer.batch_decode(out[0], skip_special_tokens=True)

    return postprocess(out_text[0])


input_text0 = "你好世界是什么意思"
input_text = "用户：" + input_text0 + "\n小元："
print(f"示例".center(50, "="))
output_text = answer(input_text)
print(f"{input_text}{output_text}\n")
