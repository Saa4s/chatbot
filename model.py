import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import pad_sequences
from tensorflow.keras import utils

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding
from tensorflow.keras.utils import pad_sequences
from tensorflow.keras import utils


import numpy as np
import pandas as pd

with open('C:\Users\sasha\Desktop\chat\dialogs.txt', 'r') as f:
  lines = [i.strip() for i in f]
questions = np.array(lines[:-1])
answers = np.array(list(map(lambda x: f'[START] {x} [END]', lines[1:])))

vocabulary_size = 5000
tokenizer = Tokenizer(num_words=vocabulary_size,  oov_token = 'unk')
tokenizer.fit_on_texts(answers[:1001])
vocabluary_items = list(tokenizer.word_index.items())
vocabulary_size = len(vocabluary_items) + 1

batch_size = 64
epochs = 100
latent_dim = 256 # скрытая размерность
num_samples = 1000
embedding_dim = 256  # Размерность эмбеддинга
# max_len = 20


def prepare_data(phrases):
  tokenized = tokenizer.texts_to_sequences(phrases)
  max_len = max([ len(x) for x in tokenized])
  # max_len = 20

  padded = pad_sequences(tokenized, maxlen=max_len, padding='post')
  encoded = np.array(padded)
  return encoded, max_len


phrases = answers[:1001][1:]
tokenized = tokenizer.texts_to_sequences(phrases)
padded = pad_sequences(tokenized, maxlen=max_len_answ, padding='post')
decoder_output = utils.to_categorical(padded, vocabulary_size)


encoder_inputs = Input(shape=(max_len_quest))
encoder_embedding = Embedding(vocabulary_size, embedding_dim)(encoder_inputs)
encoder = LSTM(latent_dim, return_state=True)
encoder_outputs, state_h, state_c = encoder(encoder_embedding)
encoder_states = [state_h, state_c]

decoder_inputs = Input(shape=(max_len_answ))
decoder_embedding = Embedding(vocabulary_size, embedding_dim)(decoder_inputs)
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
decoder_dense = Dense(vocabulary_size, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='adam', loss='categorical_crossentropy')
model.fit([encoder_input, decoder_input], decoder_output,
          batch_size=batch_size,
          epochs=epochs,
          validation_split=0.2)


encoder_model = Model(encoder_inputs, encoder_states)
decoder_state_input_h = Input(shape=(latent_dim,))
decoder_state_input_c = Input(shape=(latent_dim,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
decoder_outputs, state_h, state_c = decoder_lstm(decoder_embedding, initial_state=decoder_states_inputs)
decoder_states = [state_h, state_c]
decoder_outputs = decoder_dense(decoder_outputs)
decoder_model = Model([decoder_inputs] + decoder_states_inputs,
                      [decoder_outputs] + decoder_states)


def encode(target_seq, max_len):
  tokenized = tokenizer.texts_to_sequences(target_seq)
  padded = pad_sequences(tokenized, maxlen=max_len, padding='post')
  return np.array(padded)


def decode_sequence(input_seq, max_len):
  target_seq = encode(['[START]'], max_len)
  print(target_seq)
  stop_condition = False
  decoded_sentence = ''
  while not stop_condition:
    output_tokens, h, c = decoder_model.predict([target_seq] + states_value)
    sampled_token_index = np.argmax(output_tokens[0, -1, :])
    print(output_tokens)
    sampled_char = tokenizer.sequences_to_texts([str(sampled_token_index)])
    print(sampled_char)
    decoded_sentence += str(sampled_char)
    if (sampled_char == '[START]' or len(decoded_sentence) > max_len):
      stop_condition = True
    states_value = [h, c]
    target_seq = encode([sampled_char], max_len)
  return decoded_sentence


