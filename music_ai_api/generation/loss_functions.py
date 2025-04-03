import tensorflow as tf

def mse_with_positive_pressure(y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
    """MSE loss with additional penalty for negative predictions"""
    mse = (y_true - y_pred) ** 2
    positive_pressure = 10 * tf.maximum(-y_pred, 0.0)
    return tf.reduce_mean(mse + positive_pressure)

def percentile_loss(y_true: tf.Tensor, y_pred: tf.Tensor, percentile_factor: float = 0.2) -> tf.Tensor:
    """Loss function that encourages wider range of predictions"""
    mse = tf.square(y_true - y_pred)
    batch_min = tf.reduce_min(y_pred)
    batch_max = tf.reduce_max(y_pred)
    batch_range = batch_max - batch_min + 1e-5
    range_penalty = percentile_factor * tf.exp(-batch_range * 10.0)
    positive_pressure = 5.0 * tf.maximum(-y_pred, 0.0)
    return tf.reduce_mean(mse + range_penalty + positive_pressure)

def diversity_loss(y_true: tf.Tensor, y_pred: tf.Tensor, mean_penalty: float = 2.0) -> tf.Tensor:
    """Loss function that encourages diversity in predictions"""
    mse = tf.square(y_true - y_pred)
    batch_mean = tf.reduce_mean(y_pred)
    clustering_penalty = mean_penalty * tf.exp(-tf.abs(y_pred - batch_mean) * 5.0)
    positive_pressure = 5.0 * tf.maximum(-y_pred, 0.0)
    return tf.reduce_mean(mse + clustering_penalty + positive_pressure)
