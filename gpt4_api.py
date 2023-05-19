from automationGPT import ChatGPT
import re
import fitz
import time
from typing import List
import logging
from notionAPI import NotionAPI

class GPT4API:
    def __init__(self, api: ChatGPT, session_token: str, notion: NotionAPI, model: str = '4', sticky_model: bool = True):
        self.pdfs: List[str] = []
        self._sticky_model = sticky_model
        self._model = model
        self._notion = notion
        self._session_token: str = session_token
        self.api = api
        self.__init_logger(True)

    def __init_logger(self, verbose: bool) -> None:
        '''
        Initialize the logger\n
        :param verbose: Whether to enable verbose logging
        '''
        self.logger = logging.getLogger('GPT4API')
        self.logger.setLevel(logging.DEBUG)
        if verbose:
            formatter = logging.Formatter('[%(funcName)s] %(message)s')
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

    @staticmethod
    def preprocess(text: str) -> str:
        text = text.replace('\n', ' ')
        text = re.sub('\s+', ' ', text)
        return text

    @staticmethod
    def get_pdf_text(path: str, start_page: int = 1, end_page: int = None) -> List[str]:
        doc = fitz.open(path)
        total_pages = doc.page_count

        if end_page is None:
            end_page = total_pages

        text_list = []

        for i in range(start_page - 1, end_page):
            text = doc.load_page(i).get_text("text")
            text = GPT4API.preprocess(text)
            text_list.append(text)

        doc.close()
        return text_list

    @staticmethod
    def text_to_chunks(texts: List[str], word_length: int = 150, start_page: int = 1) -> List[str]:
        text_toks = [t.split(' ') for t in texts]

        chunks = []

        for idx, words in enumerate(text_toks):
            for i in range(0, len(words), word_length):
                chunk = words[i: i + word_length]
                if (
                    (i + word_length) > len(words)
                    and (len(chunk) < word_length)
                    and (len(text_toks) != (idx + 1))
                ):
                    text_toks[idx + 1] = chunk + text_toks[idx + 1]
                    continue
                chunk = ' '.join(chunk).strip()
                chunk = f'[Page no. {idx+start_page}]' + \
                    ' ' + '"' + chunk + '"'
                chunks.append(chunk)
        return chunks

    def _generate_text(self, message: str) -> str:
        return self.api.send_message(message)['message']

    def generate_answer(self, chunks: List[str], chunks_idxs: List[int], message_prompt_list: List[str], datasize: int = 1000) -> str:
        answer = ""
        chunks_idx = chunks_idxs[0]
        chunks_idx_idx = chunks_idxs[1]
        data_prompt = ""
        while (len(data_prompt) < datasize and chunks_idx < len(chunks)):
            remaining = min(datasize-len(data_prompt),
                            len(chunks[chunks_idx])-chunks_idx_idx)
            data_prompt += chunks[chunks_idx][chunks_idx_idx:
                                              chunks_idx_idx+remaining] + '\n\n'
            chunks_idx_idx += remaining
            if (chunks_idx_idx == len(chunks[chunks_idx])):
                chunks_idx_idx = 0
                chunks_idx += 1
        for message_prompt in message_prompt_list:
            prompt = data_prompt+message_prompt
            a = self._generate_text(prompt)
            answer += a
            answer += '\n\n'
        chunks_idxs[0] = chunks_idx
        chunks_idxs[1] = chunks_idx_idx
        return answer

    def _regenerate_session(self) -> None:
        while True:
            if self._sticky_model:
                time.sleep(3600)
            try:
                self.api.refresh_chat_page()
            except Exception as e:
                self.logger.error(f'Could not quit api. {e}')

    def parsePDF(self, name: str, doc_path_name: str, prompts: List[str], first_chunks_idxs: List[int] = [0, 0]):
        texts = GPT4API.get_pdf_text(doc_path_name, start_page=1)
        chunks = GPT4API.text_to_chunks(texts, start_page=1)
        blocks = [f'***Notes for {name}***\n\n']
        chunks_idxs = first_chunks_idxs
        while (chunks_idxs[0] <= len(chunks)):
            try:
                ans = self.generate_answer(chunks, chunks_idxs, prompts)
                blocks.append(ans)
                with open(f'out/{name}.txt', 'a') as f:
                    f.write(ans)
                self._notion.delete_page(name)
                self._notion.create_page(name, blocks)
                self.logger.debug(
                    f"Output produced: {chunks_idxs[0]} \n {ans}")
            except Exception as e:
                self.logger.error(e)
                self._regenerate_session()
        
        self.api.refresh_chat_page()
