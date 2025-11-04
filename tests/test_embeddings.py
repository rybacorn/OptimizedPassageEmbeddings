import sys
import types
from pathlib import Path

import numpy as np
import pytest

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from passage_embed.analysis.embeddings import EmbeddingGenerator
from passage_embed.cli import DEFAULT_MODEL_NAME, resolve_model_name


class FakeSentenceTransformer:
    """Lightweight stand-in for SentenceTransformer during tests."""

    instances = []

    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.init_kwargs = kwargs
        self.encode_calls = []
        self.encode_document_calls = []
        self.encode_query_calls = []
        FakeSentenceTransformer.instances.append(self)

    def _dim(self) -> int:
        return 768 if 'embeddinggemma' in self.model_name else 384

    def encode(self, texts):
        self.encode_calls.append(texts)
        dim = self._dim()
        base = np.arange(dim, dtype=np.float32)
        if isinstance(texts, list):
            return np.tile(base, (len(texts), 1))
        return base

    def encode_document(self, texts):
        self.encode_document_calls.append(texts)
        dim = self._dim()
        base = np.arange(dim, dtype=np.float32) + 1.0
        if isinstance(texts, list):
            return np.tile(base, (len(texts), 1))
        return base

    def encode_query(self, texts):
        self.encode_query_calls.append(texts)
        dim = self._dim()
        base = np.arange(dim, dtype=np.float32) + 2.0
        return np.tile(base, (len(texts), 1))


@pytest.fixture(autouse=True)
def patch_sentence_transformer(monkeypatch):
    """Replace SentenceTransformer with a deterministic fake."""

    FakeSentenceTransformer.instances.clear()
    monkeypatch.setattr(
        'passage_embed.analysis.embeddings.SentenceTransformer',
        FakeSentenceTransformer,
    )

    torch_stub = types.SimpleNamespace(bfloat16='bfloat16', float32='float32')
    original_torch = sys.modules.get('torch')
    sys.modules['torch'] = torch_stub

    try:
        yield FakeSentenceTransformer
    finally:
        if original_torch is not None:
            sys.modules['torch'] = original_torch
        else:
            sys.modules.pop('torch', None)
        FakeSentenceTransformer.instances.clear()


def test_resolve_model_name_presets():
    assert resolve_model_name('fast') == 'all-MiniLM-L6-v2'
    assert resolve_model_name('multilingual') == 'paraphrase-multilingual-mpnet-base-v2'


def test_resolve_model_name_default():
    assert resolve_model_name(None) == DEFAULT_MODEL_NAME


def test_embedding_gemma_loads_with_bfloat16():
    EmbeddingGenerator(model_name='google/embeddinggemma-300m')
    fake_model = FakeSentenceTransformer.instances[-1]
    assert fake_model.init_kwargs.get('model_kwargs') == {'torch_dtype': 'bfloat16'}


def test_mrl_truncation_applies_for_queries():
    generator = EmbeddingGenerator(model_name='google/embeddinggemma-300m', embedding_dim=256)
    query_data, mean_vector = generator.generate_query_embeddings(['one', 'two'])

    assert all(item['embedding'].shape == (256,) for item in query_data)
    assert mean_vector.shape == (256,)
    fake_model = FakeSentenceTransformer.instances[-1]
    assert fake_model.encode_query_calls == [['one', 'two']]


def test_process_json_uses_document_encoding_for_gemma():
    generator = EmbeddingGenerator(model_name='google/embeddinggemma-300m', embedding_dim=768)
    json_data = {
        'client': [
            {'type': 'p', 'value': 'Example paragraph.', 'source': 'client'},
            {'type': 'h1', 'value': 'Sample heading', 'source': 'client'},
        ]
    }
    symbol_mapping = {'client': 'circle'}
    size_mapping = {'client': 8}

    embeddings_data, mean_embeddings = generator.process_json_data(
        json_data,
        symbol_mapping,
        size_mapping,
    )

    fake_model = FakeSentenceTransformer.instances[-1]
    assert len(fake_model.encode_document_calls) == 2
    assert len(fake_model.encode_calls) == 0
    assert embeddings_data[0]['embedding'].shape == (768,)
    assert mean_embeddings['client'].shape == (768,)


def test_non_gemma_models_retain_original_dimension():
    generator = EmbeddingGenerator(model_name='all-MiniLM-L6-v2')
    embeddings = generator.generate_embeddings(['sample text'])

    assert embeddings.shape == (1, 384)


def test_generate_embeddings_truncates_documents():
    generator = EmbeddingGenerator(model_name='google/embeddinggemma-300m', embedding_dim=128)
    embeddings = generator.generate_embeddings(['one text', 'two text'])

    assert embeddings.shape == (2, 128)
    # Verify normalization after truncation
    row_norms = np.linalg.norm(embeddings, axis=1)
    assert np.allclose(row_norms, 1.0)

