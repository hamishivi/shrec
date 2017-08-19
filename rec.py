from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
from pyspark import SparkContext
from pyspark import RDD
import pyspark

from pprint import pprint as pp


sc = SparkContext()
try:
    model = MatrixFactorizationModel.load(sc, "CF.model")
except Exception:
    model = None

def main():
    data = load_file("training_data")
    model = train(data)
    '''
    # Evaluate the model on training data
    testdata = ratings.map(lambda p: (p[0], p[1]))
    predictions = model.predictAll(testdata).map(lambda r: ((r[0], r[1]), r[2]))
    ratesAndPreds = ratings.map(lambda r: ((r[0], r[1]), r[2])).join(predictions)
    MSE = ratesAndPreds.map(lambda r: (r[1][0] - r[1][1])**2).mean()
    print("Mean Squared Error = " + str(MSE))
    '''
    pp(data)
    pp(get_rec(int_hash(76561198067457280)))

def train(data):
    '''
    take data -> produces model
    '''
    global model
    rank = 10
    numIterations = 10
    model = ALS.trainImplicit(data, rank, numIterations)
    model.save(sc, "CF.model")

    return model

def get_rec(user, num_rec=10):
    global model
    return model.recommendProducts(user, num_rec)

def load_file(filename):
    global sc
    return sc.textFile(filename).map(lambda l: l.split(',')).map(lambda l: Rating(int_hash(int(l[0])), int(l[1]), float(l[2])))

def format_data(data_list):
    '''
    data_list contains (user, game, playtime) tuples
    '''
    global sc
    return sc.parallelize(data_list).map(lambda r: Rating(int_hash(r[0]), int(r[1]), int(r[2])))

def int_hash(s):
    return hash(s) % 2147483647

main()
