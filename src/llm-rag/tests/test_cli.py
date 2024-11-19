import pytest
from unittest.mock import Mock, patch, mock_open
import pandas as pd
import os
import json
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter


# Mock Setup
patch_dict = patch.dict('os.environ', {
    'GCP_PROJECT': 'mock-project',
    'GCP_LOCATION': 'mock-location'
})
patch_init = patch('vertexai.init')
patch_embedding = patch('vertexai.language_models.TextEmbeddingModel.from_pretrained')
patch_generative = patch('vertexai.generative_models.GenerativeModel')

# Start all patches
patch_dict.start()
patch_init.start()
patch_embedding.start()
patch_generative.start()

from cli import (
    generate_query_embedding,
    generate_text_embeddings,
    load_text_embeddings,
    city_mappings,
    chunk,
    embed,
    load, 
    query,
    chat,
    get
)


class TestEmbeddings:

    @pytest.fixture
    def sample_dataframe(self):
        """Fixture to create a sample testing DataFrame"""
        data = {
            'chunk': ['chunk 1 for testing', 'test chunk 2 for testing'],
            'city': ['Amsterdam', 'Amsterdam'],
            'embedding': [[0.1] * 256, [0.1] * 256]
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def mock_collection(self):
        """Fixture to create mock ChromaDB collection"""
        mock_collection = Mock()
        mock_collection.name = "test-collection"
        return mock_collection

    def test_city_mappings_content(self):
        """Test if city_mappings contains correct data"""
        assert "Amsterdam" in city_mappings
        assert city_mappings["Amsterdam"]["country"] == "Netherlands"
        assert city_mappings["Amsterdam"]["continent"] == "Europe"

    
    def test_generate_query_embedding_construction(self):
        """Test if query embedding is constructed with correct parameters"""
        with patch('cli.embedding_model') as mock_model:
            # Set up mock embedding 
            mock_embedding = Mock()
            mock_embedding.values = [0.1] * 256
            mock_model.get_embeddings.return_value = [mock_embedding]
            
            # Call the function
            query = "This is a test query"
            result = generate_query_embedding(query)

            args = mock_model.get_embeddings.call_args.args
            kwargs = mock_model.get_embeddings.call_args.kwargs
            embedding_input = args[0][0]  
            
            # Verify input parameters
            assert embedding_input.text == "This is a test query"
            assert embedding_input.task_type == "RETRIEVAL_DOCUMENT"
            assert kwargs == {"output_dimensionality": 256}
            assert result == [0.1] * 256


    def test_generate_text_embeddings_batch_processing(self):
        """Test batching operation of generate_text_embeddings"""
        chunks = ["chunk1", "chunk2", "chunk3"]
        batch_size = 2
        
        with patch('cli.embedding_model.get_embeddings') as mock_get_embeddings:
            generate_text_embeddings(chunks, batch_size=batch_size)
            
            # Verify batching logic
            # Should be called twice for 3 items with batch_size 2
            assert mock_get_embeddings.call_count == 2  
            
            # Verify first batch had 2 items, second batch had 1 item
            first_call_args = mock_get_embeddings.call_args_list[0][0][0]
            second_call_args = mock_get_embeddings.call_args_list[1][0][0]
            assert len(first_call_args) == 2
            assert first_call_args[0].text == 'chunk1'
            assert first_call_args[1].text == 'chunk2'
            assert len(second_call_args) == 1
            assert second_call_args[0].text == 'chunk3'


    def test_load_text_embeddings(self, sample_dataframe, mock_collection):
        """Test load_text_embeddings function"""
        load_text_embeddings(sample_dataframe, mock_collection)
        
        mock_collection.add.assert_called() # Check if method was called
        call_args = mock_collection.add.call_args[1]
        
        # Verify argument structure
        assert 'ids' in call_args
        assert 'documents' in call_args
        assert 'metadatas' in call_args
        assert 'embeddings' in call_args
        
        # Verify result structure (metadatas, documents, ids)
        assert call_args['metadatas'][0]['city'] == 'Amsterdam'
        assert call_args['metadatas'][0]['country'] == 'Netherlands'
        assert call_args['metadatas'][0]['continent'] == 'Europe'
        assert call_args['documents'] == ['chunk 1 for testing', 'test chunk 2 for testing']
        assert len(call_args['embeddings'][0]) == 256
        assert len(call_args['ids']) == 2
        assert all(len(id.split('-')) == 2 for id in call_args['ids']) 
        all(len(id.split('-')[0]) == 16 for id in call_args['ids'])


class TestChunkFunction:
    @pytest.fixture
    def mock_file_content(self):
        return "This is a test content for the city of Amsterdam." * 10

    @pytest.fixture
    def mock_glob(self):
        with patch('glob.glob') as mock:
            mock.return_value = ['input-datasets/cities-wiki/Amsterdam.txt']
            yield mock

    def test_chunk_char_split(self, mock_glob, mock_file_content):
        """Test chunk function with char-split method"""
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mocked_file:
            with patch('os.makedirs') as mock_makedirs:
                chunk(method="char-split")

                # Verify directory was created
                mock_makedirs.assert_called_once_with('outputs', exist_ok=True)

                # Get the JSON string that was written
                json_str = mocked_file.return_value.write.call_args.args[0]
                
                # Convert JSON string to dictionary
                chunks = [json.loads(line) for line in json_str.strip().split('\n')]
                
                # Verify each chunk is a dictionary with the expected structure
                for text_dict in chunks:
                    assert isinstance(text_dict, dict)
                    assert 'chunk' in text_dict
                    assert 'city' in text_dict
                    assert text_dict['city'] == 'Amsterdam'
                    
                    
              

    def test_chunk_recursive_split(self, mock_glob, mock_file_content):
        """Test chunk function with recursive-split method"""
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mocked_file:
            with patch('os.makedirs') as mock_makedirs:
                chunk(method="recursive-split")

                # Verify directory was created
                mock_makedirs.assert_called_once_with('outputs', exist_ok=True)

                # Get the JSON string that was written
                json_str = mocked_file.return_value.write.call_args.args[0]
                
                # Convert JSON string to dictionary
                chunks = [json.loads(line) for line in json_str.strip().split('\n')]
                
                # Verify each chunk is a dictionary with the expected structure
                for text_dict in chunks:
                    assert isinstance(text_dict, dict)
                    assert 'chunk' in text_dict
                    assert 'city' in text_dict
                    assert text_dict['city'] == 'Amsterdam'


    def test_chunk_semantic_split(self, mock_glob, mock_file_content):
        """Test chunk function with semantic-split method"""
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mocked_file:
            with patch('os.makedirs') as mock_makedirs:
                chunk(method="semantic-split")

                # Verify directory calling
                mock_makedirs.assert_called_once_with('outputs', exist_ok=True)

                # Get the JSON string that was written
                json_str = mocked_file.return_value.write.call_args.args[0]
                
                # Convert JSON string to dictionary
                chunks = [json.loads(line) for line in json_str.strip().split('\n')]
                
                # Verify each chunk is a dictionary with the expected structure
                for text_dict in chunks:
                    assert isinstance(text_dict, dict)
                    assert 'chunk' in text_dict
                    assert 'city' in text_dict
                    assert text_dict['city'] == 'Amsterdam'
                    

class TestEmbedFunction:
    @pytest.fixture
    def mock_jsonl_content(self):
        data = [
            {'chunk': 'test chunk 1', 'city': 'Amsterdam'},
            {'chunk': 'test chunk 2', 'city': 'Amsterdam'}
        ]
        return '\n'.join(json.dumps(d) for d in data)
    

    @pytest.fixture
    def mock_glob(self):
        with patch('glob.glob') as mock:
            mock.return_value = ['outputs/chunks-char-split-Amsterdam.jsonl']
            yield mock

    def test_embed_char_split(self, mock_glob, mock_jsonl_content):
        """Test embed function with char-split method"""
        with patch('pandas.read_json'):
            with patch('cli.generate_text_embeddings') as mock_gen_embed:
                mock_gen_embed.return_value = [[0.1] * 256, [0.1] * 256]
                with patch('builtins.open', mock_open()):
                    embed(method="char-split")
                    mock_gen_embed.assert_called_once()

    def test_embed_semantic_split(self, mock_glob, mock_jsonl_content):
        """Test embed function with semantic-split method"""
        with patch('pandas.read_json'):
            with patch('cli.generate_text_embeddings') as mock_gen_embed:
                mock_gen_embed.return_value = [[0.1] * 256, [0.1] * 256]
                with patch('builtins.open', mock_open()):
                    embed(method="semantic-split")
                    mock_gen_embed.assert_called_once()



class TestLoadFunction:
    @pytest.fixture
    def mock_chromadb_client(self):
        with patch('chromadb.HttpClient') as mock:
            client = Mock()
            collection = Mock()
            client.create_collection.return_value = collection
            mock.return_value = client
            yield mock

    @pytest.fixture
    def mock_glob(self):
        with patch('glob.glob') as mock:
            mock.return_value = ['outputs/embeddings-char-split-Amsterdam.jsonl']
            yield mock

    def test_load_success(self, mock_chromadb_client, mock_glob):
        """Test load function with successful connection"""
        with patch('pandas.read_json'):
            with patch('cli.load_text_embeddings') as mock_load:
                load(method="char-split")
                mock_load.assert_called_once()

    def test_load_collection_exists(self, mock_chromadb_client, mock_glob):
        """Test load function when collection exists"""
        client = mock_chromadb_client.return_value
        client.delete_collection.side_effect = Exception()
        
        with patch('pandas.read_json'):
            with patch('cli.load_text_embeddings'):
                load(method="char-split")
                client.create_collection.assert_called_once()

    def test_load_no_files(self):
        """Test load function with no files to process"""
        with patch('glob.glob') as mock_glob:
            mock_glob.return_value = []
            with patch('chromadb.HttpClient'):
                load(method="char-split")
                assert mock_glob.called
                
                
                
class TestQueryFunction:
    @pytest.fixture
    def mock_chromadb_client(self):
        with patch('chromadb.HttpClient') as mock:
            client = Mock()
            collection = Mock()
            collection.query.return_value = {
                "documents": [["test document"]],
                "metadatas": [{"city": "Beijing"}],
                "distances": [0.1]
            }
            client.get_collection.return_value = collection
            mock.return_value = client
            yield mock

    def test_query_basic(self, mock_chromadb_client):
        """Test basic query functionality"""
        with patch('cli.generate_query_embedding') as mock_gen_embed:
            mock_gen_embed.return_value = [0.1] * 256
            query(method="char-split")
            
            # Verify query was called three times (basic, metadata filter, lexical search)
            collection = mock_chromadb_client.return_value.get_collection.return_value
            assert collection.query.call_count == 3

    def test_query_with_metadata_filter(self, mock_chromadb_client):
        """Test query with metadata filter"""
        with patch('cli.generate_query_embedding') as mock_gen_embed:
            mock_gen_embed.return_value = [0.1] * 256
            query(method="char-split")
            
            collection = mock_chromadb_client.return_value.get_collection.return_value
            calls = collection.query.call_args_list
            
            # Check the second call (metadata filter)
            assert calls[1][1]['where'] == {"city": "London"}

    def test_query_with_lexical_search(self, mock_chromadb_client):
        """Test query with lexical search"""
        with patch('cli.generate_query_embedding') as mock_gen_embed:
            mock_gen_embed.return_value = [0.1] * 256
            query(method="char-split")
            
            collection = mock_chromadb_client.return_value.get_collection.return_value
            calls = collection.query.call_args_list
            
            # Check the third call (lexical search)
            assert calls[2][1]['where_document'] == {"$contains": "Italian"}                


class TestChatFunction:
    @pytest.fixture
    def mock_chromadb_client(self):
        with patch('chromadb.HttpClient') as mock:
            client = Mock()
            collection = Mock()
            collection.query.return_value = {
                "documents": [["test document"]],
                "metadatas": [{"city": "Beijing"}],
                "distances": [0.1]
            }
            client.get_collection.return_value = collection
            mock.return_value = client
            yield mock

    def test_chat_basic(self, mock_chromadb_client):
        """Test basic chat functionality"""
        with patch('cli.generate_query_embedding') as mock_gen_embed:
            with patch('cli.generative_model.generate_content') as mock_generate:
                mock_gen_embed.return_value = [0.1] * 256
                mock_response = Mock()
                mock_response.text = "Test response"
                mock_generate.return_value = mock_response
                
                chat(method="char-split")
                
                # Verify ChromaDB query was called
                collection = mock_chromadb_client.return_value.get_collection.return_value
                collection.query.assert_called_once()
                
                # Verify generative model was called
                mock_generate.assert_called_once()

class TestGetFunction:
    @pytest.fixture
    def mock_chromadb_client(self):
        with patch('chromadb.HttpClient') as mock:
            client = Mock()
            collection = Mock()
            collection.get.return_value = {
                "documents": ["test document"],
                "metadatas": [{"city": "London"}],
                "ids": ["test-id"]
            }
            client.get_collection.return_value = collection
            mock.return_value = client
            yield mock

    def test_get_documents(self, mock_chromadb_client):
        """Test getting documents from collection"""
        get(method="char-split")
        
        collection = mock_chromadb_client.return_value.get_collection.return_value
        collection.get.assert_called_once_with(
            where={"city": "London"},
            limit=10
        )