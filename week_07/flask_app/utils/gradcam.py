import tensorflow as tf
import numpy as np
import cv2
import os


def find_last_conv_layer(model):
    """
    Returns the last convolutional layer for ResNet50.
    """

    try:
        return model.get_layer("conv5_block3_out")
    except Exception:
        # Fallback for other CNN models
        conv_layers = []

        def search(layer):
            if isinstance(layer, tf.keras.layers.Conv2D):
                conv_layers.append(layer)

            elif isinstance(layer, tf.keras.Model):
                for sub_layer in layer.layers:
                    search(sub_layer)

        search(model)

        if len(conv_layers) == 0:
            return None

        return conv_layers[-1]


def generate_gradcam(model, img_array, save_path, class_index=None):
    """
    Generates Grad-CAM heatmap.

    Parameters
    ----------
    model : keras model

    img_array : image with shape
                (1,224,224,3)

    save_path : output image path

    class_index : Optional.
                  If None, predicted class is used.
    """

    # Forward pass
    predictions = model.predict(img_array, verbose=0)

    if class_index is None:
        class_index = np.argmax(predictions[0])

    last_conv_layer = find_last_conv_layer(model)

    if last_conv_layer is None:
        raise Exception("No convolution layer found.")

    print("Using GradCAM Layer:", last_conv_layer.name)

    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[
            last_conv_layer.output,
            model.output
        ]
    )

    with tf.GradientTape() as tape:

        conv_outputs, predictions = grad_model(img_array)

        loss = predictions[:, class_index]

    gradients = tape.gradient(loss, conv_outputs)

    pooled_gradients = tf.reduce_mean(
        gradients,
        axis=(0, 1, 2)
    )

    conv_outputs = conv_outputs[0]

    heatmap = tf.reduce_sum(
        conv_outputs * pooled_gradients,
        axis=-1
    )

    heatmap = tf.maximum(heatmap, 0)

    if tf.reduce_max(heatmap) != 0:
        heatmap /= tf.reduce_max(heatmap)

    heatmap = heatmap.numpy()

    height = img_array.shape[1]
    width = img_array.shape[2]

    heatmap = cv2.resize(
        heatmap,
        (width, height)
    )

    heatmap = np.uint8(255 * heatmap)

    heatmap = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    img = img_array[0]

    img = np.clip(img, 0, 1)

    img = np.uint8(img * 255)

    output = cv2.addWeighted(
        img,
        0.6,
        heatmap,
        0.4,
        0
    )

    os.makedirs(
        os.path.dirname(save_path),
        exist_ok=True
    )

    cv2.imwrite(
        save_path,
        cv2.cvtColor(
            output,
            cv2.COLOR_RGB2BGR
        )
    )

    return save_path