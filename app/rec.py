import os.path
from shutil import rmtree
from py4j.protocol import Py4JJavaError
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
from pyspark import SparkContext
from pyspark import RDD

from pprint import pprint as pp

sc = SparkContext()
sc.setLocalProperty('spark.ui.enabled', 'false')
sc.setLogLevel('ERROR')

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
    pp(get_rec(76561198067457280))

def train(data):
    '''
    take data -> produces model
    '''
    global model
    rank = 10
    numIterations = 10
    model = ALS.trainImplicit(data, rank, numIterations)
    if os.path.exists("CF.model"):
        rmtree("CF.model")
    model.save(sc, "CF.model")

    return model

def get_rec(user, num_rec=10):
    global model
    user_hash = int_hash(user)
    try:
        return model.recommendProducts(user_hash, num_rec)
    except Py4JJavaError:
        return None

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


#main()
