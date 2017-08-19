from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
from pyspark import SparkContext
from pprint import pprint as pp

def main():

    sc = SparkContext()
    # Load and parse the data
    data = sc.textFile("training_data")
    ratings = data.map(lambda l: l.split(','))\
    .map(lambda l: Rating(int_hash(int(l[0])), int(l[1]), int(l[2])))

    # Build the recommendation model using Alternating Least Squares
    rank = 10
    numIterations = 10
    model = ALS.train(ratings, rank, numIterations)

    # Evaluate the model on training data
    testdata = ratings.map(lambda p: (p[0], p[1]))
    predictions = model.predictAll(testdata).map(lambda r: ((r[0], r[1]), r[2]))
    ratesAndPreds = ratings.map(lambda r: ((r[0], r[1]), r[2])).join(predictions)
    MSE = ratesAndPreds.map(lambda r: (r[1][0] - r[1][1])**2).mean()
    print("Mean Squared Error = " + str(MSE))

    # Save and load modeil
    # model.save(sc, "CF.model")
    # model = MatrixFactorizationModel.load(sc, "CF.model")
    user_recs = model.recommendProducts(int_hash(76561198067457280), 10)
    pp(user_recs)

def int_hash(s):
    return hash(s) % 2147483647

main()
