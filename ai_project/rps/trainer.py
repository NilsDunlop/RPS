# Importing Libraries
import os
import pandas as pd
import numpy as np
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from keras.optimizers import Adam
from datetime import date


# Method that trains on the current data in ./data folder and creates a new model.
# Method returns the name of the model, the result of the model and the path the where to model is stored
def train_model():
    current_folder = os.getcwd()
    base_dir = os.path.join(current_folder, 'data')

    # Train directory path
    train_dir = os.path.join(base_dir, 'train')

    # Test directory path
    test_dir = os.path.join(base_dir, 'test')

    # Validation directory path
    validation_dir = os.path.join(base_dir, 'validation')

    # Step 1: Creating the CNN model
    model = Sequential()

    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(150, 150, 3)))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(2, 2))

    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D(2, 2))

    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D(2, 2))

    model.add(Flatten())
    model.add(Dropout(0.4))
    model.add(Dense(512, activation='relu'))
    model.add(Dense(3, activation='softmax'))

    model.compile(loss='categorical_crossentropy',
                  optimizer=keras.optimizers.Adam(),
                  metrics=['accuracy'])
    model.summary()

    # Step 2: Create image data generators
    # ImageDataGenerator to decode the PNG images to RGB grids of pixels as well as to augment
    # the images using parameters for rescaling, resizing, rotating and mirroring etc
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=40,
        width_shift_range=0.2,  # Shift image width by 20%
        height_shift_range=0.2,  # Shift image height by 20%
        shear_range=0.2,  # Rotate x-axis by 20%
        zoom_range=0.2,  # Zoom image by 20%
        horizontal_flip=True,
        fill_mode='nearest')

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(150, 150),
        class_mode='categorical',
        batch_size=20
    )
    nr_im_train = len(train_generator.filenames)

    validation_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)

    validation_generator = validation_datagen.flow_from_directory(
        test_dir,
        target_size=(150, 150),
        class_mode='categorical',
        batch_size=20
    )
    nr_im_test = len(validation_generator.filenames)

    # Step 3: Train the model
    history = model.fit(
        train_generator,
        steps_per_epoch=np.ceil(nr_im_train / 20),
        epochs=5,
        validation_data=validation_generator,
        validation_steps=np.ceil(nr_im_test / 20),
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True)],
        verbose=2)

    # Step 4: Testing the model
    test_img = os.listdir(os.path.join(validation_dir))
    test_df = pd.DataFrame({'Image': test_img})

    test_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)

    test_generator = test_gen.flow_from_dataframe(test_df, validation_dir, x_col='Image', y_col=None, class_mode=None,
                                                  target_size=(150, 150), batch_size=20, shuffle=False)
    nr_im_val = len(test_generator.filenames)

    predict = model.predict(test_generator, steps=int(np.ceil(nr_im_val / 20)))

    label_map = dict((v, k) for k, v in train_generator.class_indices.items())

    test_df['Label'] = np.argmax(predict, axis=-1)
    test_df['Label'] = test_df['Label'].replace(label_map)

    # Get the result of the model
    final_list = []
    for index in test_df.index:
        if test_df['Label'][index] in test_df['Image'][index]:
            final_list.append(1)
        else:
            final_list.append(0)
    result = round(sum(final_list) / len(final_list) * 100, 2)
    filename = 'model_result=' + str(result) + '.Date=' + str(date.today()) + '.h5'
    path = './media/uploaded_models/' + filename
    if result >= 90.00:
        model.save(path)

    return filename, path, result
