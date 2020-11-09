import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import random
import json
import pickle
import socket
import speech_recognition

with open("instructions.json") as file:
    data = json.load(file)

words = []
labels = []
docs_x = []
docs_y = []

for intent in data["instructions"]:
    for patterns in intent["patterns"]:
        wrds = nltk.word_tokenize(patterns)
        words.extend(wrds)
        docs_x.append(wrds)
        docs_y.append(intent["tag"])

    if intent["tag"] not in labels:
            labels.append(intent["tag"])

words = [stemmer.stem(w.lower()) for w in words if w != "?"]
words = sorted(list(set(words)))

labels = sorted(labels)

training = []
output = []

out_empty = [0 for _ in range(len(labels))]

for x,doc in enumerate(docs_x):
    bag = []

    wrds = [stemmer.stem(w) for w in doc]

    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)

    output_row = out_empty[:]
    output_row[labels.index(docs_y[x])] = 1

    training.append(bag)
    output.append(output_row)

training = numpy.array(training)
output = numpy.array(output)

with open("data.pickle", "wb") as f:
    pickle.dump((words, labels, training, output), f)

tensorflow.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)
                              
mod = tflearn.DNN(net)

mod.fit(training, output, n_epoch=600, batch_size=8, show_metric=True)
mod.save("mod.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i,w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)

def hear_input():
    r =  speech_recognition.Recognizer()

    with speech_recognition.Microphone() as source:
        print("Command: ")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    x = r.recognize_google(audio, key=None, language='en-US', show_all=True)
    return str(x)

def chat():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    host = socket.gethostname()
    ip_addr  = socket.gethostbyname(host)
    port = 50000
    server_socket.bind((ip_addr, port));
    print("Socket Created")
    server_socket.listen(5)
    print("Socket is listening")
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))
    print("Start talking with the bot (quit to exit model)")
    while True:
        inp = hear_input()
        if inp.lower() == "end":
            print(inp)
            conn.send("8".encode())
            conn.close()
            break

        results = mod.predict([bag_of_words(inp, words)])[0]
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        if results[results_index] > 0.50:
            print(inp + "\n" + "Command identified as: " + tag)
            conn.send(tag.encode())

        else:
            print("Not identified")
            conn.send("0".encode())

chat()

