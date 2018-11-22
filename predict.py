import pickle

file_model = open('model.pkl', 'rb')
pipeline = pickle.load(file_model)
file_model.close()


text_file = open('file.txt', 'r')
for line in text_file:
    category = pipeline.predict([line])
    print(line, category)
