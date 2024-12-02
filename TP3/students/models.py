import nn
from backend import PerceptronDataset, RegressionDataset, DigitClassificationDataset


class PerceptronModel(object):
    def __init__(self, dimensions: int) -> None:
        """
        Initialize a new Perceptron instance.

        A perceptron classifies data points as either belonging to a particular
        class (+1) or not (-1). `dimensions` is the dimensionality of the data.
        For example, dimensions=2 would mean that the perceptron must classify
        2D points.
        """
        self.w = nn.Parameter(1, dimensions)

    def get_weights(self) -> nn.Parameter:
        """
        Return a Parameter instance with the current weights of the perceptron.
        """
        return self.w

    def run(self, x: nn.Constant) -> nn.Node:
        """
        Calculates the score assigned by the perceptron to a data point x.

        Inputs:
            x: a node with shape (1 x dimensions)
        Returns: a node containing a single number (the score)
        """
        return nn.DotProduct(self.w, x)

    def get_prediction(self, x: nn.Constant) -> int:
        """
        Calculates the predicted class for a single data point `x`.

        Returns: 1 or -1
        """
        score = nn.as_scalar(self.run(x))
        if score >= 0:
            return 1
        else:
            return -1

    def train(self, dataset: PerceptronDataset) -> None:
        """
        Train the perceptron until convergence.
        """
        converged = False
        while not converged:
            converged = True
            for x, y in dataset.iterate_once(1):
                prediction = self.get_prediction(x)
                true_label = nn.as_scalar(y)
                if prediction != true_label:
                    self.w.update(x, true_label)
                    converged = False


class RegressionModel(object):
    """
    A neural network model for approximating a function that maps from real
    numbers to real numbers. The network should be sufficiently large to be able
    to approximate sin(x) on the interval [-2pi, 2pi] to reasonable precision.
    """

    def __init__(self) -> None:
        # Initialize your model parameters here
        hidden_dimensions = 150

        self.W1 = nn.Parameter(1, hidden_dimensions)
        self.b1 = nn.Parameter(1, hidden_dimensions)
        self.W2 = nn.Parameter(hidden_dimensions, 1)
        self.b2 = nn.Parameter(1, 1)

    def run(self, x: nn.Constant) -> nn.Node:
        """
        Runs the model for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
        Returns:
            A node with shape (batch_size x 1) containing predicted y-values
        """
        hidden_layer = nn.ReLU(nn.AddBias(nn.Linear(x, self.W1), self.b1))

        output = nn.AddBias(nn.Linear(hidden_layer, self.W2), self.b2)

        return output

    def get_loss(self, x: nn.Constant, y: nn.Constant) -> nn.Node:
        """
        Computes the loss for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
            y: a node with shape (batch_size x 1), containing the true y-values
                to be used for training
        Returns: a loss node
        """
        predicted_y = self.run(x)
        return nn.SquareLoss(predicted_y, y)

    def train(self, dataset: RegressionDataset) -> None:
        """
        Trains the model.
        """
        learning_rate = 0.05
        batch_size = 20
        total_loss = float("inf")
        loss_threshold = 0.02

        while total_loss > loss_threshold:
            for x_batch, y_batch in dataset.iterate_once(batch_size):

                loss = self.get_loss(x_batch, y_batch)

                gradients = nn.gradients(loss, [self.W1, self.b1, self.W2, self.b2])

                self.W1.update(gradients[0], -learning_rate)
                self.b1.update(gradients[1], -learning_rate)
                self.W2.update(gradients[2], -learning_rate)
                self.b2.update(gradients[3], -learning_rate)

            for x, y in dataset.iterate_once(dataset.y.size):
                total_loss = nn.as_scalar(self.get_loss(x, y))


class DigitClassificationModel(object):
    """
    A model for handwritten digit classification using the MNIST dataset.

    Each handwritten digit is a 28x28 pixel grayscale image, which is flattened
    into a 784-dimensional vector for the purposes of this model. Each entry in
    the vector is a floating point number between 0 and 1.

    The goal is to sort each digit into one of 10 classes (number 0 through 9).

    (See RegressionModel for more information about the APIs of different
    methods here. We recommend that you implement the RegressionModel before
    working on this part of the project.)
    """

    def __init__(self) -> None:
        # Initialize your model parameters here
        self.W1 = nn.Parameter(784, 128)
        self.b1 = nn.Parameter(1, 128)
        self.W2 = nn.Parameter(128, 10)
        self.b2 = nn.Parameter(1, 10)

    def run(self, x: nn.Constant) -> nn.Node:
        """
        Runs the model for a batch of examples.

        Your model should predict a node with shape (batch_size x 10),
        containing scores. Higher scores correspond to greater probability of
        the image belonging to a particular class.

        Inputs:
            x: a node with shape (batch_size x 784)
        Output:
            A node with shape (batch_size x 10) containing predicted scores
                (also called logits)
        """
        hidden_layer = nn.ReLU(nn.AddBias(nn.Linear(x, self.W1), self.b1))

        output = nn.AddBias(nn.Linear(hidden_layer, self.W2), self.b2)

        return output

    def get_loss(self, x: nn.Constant, y: nn.Constant) -> nn.Node:
        """
        Computes the loss for a batch of examples.

        The correct labels `y` are represented as a node with shape
        (batch_size x 10). Each row is a one-hot vector encoding the correct
        digit class (0-9).

        Inputs:
            x: a node with shape (batch_size x 784)
            y: a node with shape (batch_size x 10)
        Returns: a loss node
        """
        predicted_y = self.run(x)
        return nn.SoftmaxLoss(predicted_y, y)

    def train(self, dataset: DigitClassificationDataset) -> None:
        """
        Trains the model.
        """
        learning_rate = 0.5
        batch_size = 200
        validation_accuracy = 0
        accuracy_threshold = 0.97

        while validation_accuracy < accuracy_threshold:
            for x_batch, y_batch in dataset.iterate_once(batch_size):

                loss = self.get_loss(x_batch, y_batch)

                gradients = nn.gradients(loss, [self.W1, self.b1, self.W2, self.b2])

                self.W1.update(gradients[0], -learning_rate)
                self.b1.update(gradients[1], -learning_rate)
                self.W2.update(gradients[2], -learning_rate)
                self.b2.update(gradients[3], -learning_rate)

            validation_accuracy = dataset.get_validation_accuracy()
