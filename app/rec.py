import pandas as pd
import numpy as np
import implicit
from scipy.sparse import coo_matrix

def get_rec(username, df, gameplay_time):
    '''
    get a recommendation for a user given a username (steam id), a numpy dataframe with a list of users and games, and a sparse matrix of games by users, which each cell has the amount of hours played.
    '''
    # create a model
    model = implicit.als.AlternatingLeastSquares()
    userid = None
    try:
        # get the userid mapping from the sparse matrix
        userid = df['user'].cat.categories.tolist().index(username)
    except ValueError:
        return None

    # lets weight these models by bm25weight. see https://en.wikipedia.org/wiki/Okapi_BM25
    # this essentially weights values by their relevance (ie if a game is played an unusually
    # large amount of time compared to most other people)
    # So this should ideally help stop the Valve bias - if everyone plays a lot of DOTA2, then it should
    # have a lower weight.
    plays = implicit.nearest_neighbours.bm25_weight(gameplay_time, K1=100, B=0.8)

    # converts to compressed row space (csr) format, faster for stuff.
    gameplay_time = gameplay_time.tocsr()

    # this does our 'training'
    model.fit(gameplay_time)

    games = dict(enumerate(df['game'].cat.categories))
    user_plays = plays.T.tocsr()
    # recommend games, ordered by confidence. N is the amount of reccomendations
    # the method gives, so its set to as many games as possible, so we can filter out the
    # games the user actually owns.

    recs = model.recommend(userid, user_plays, N=len(df['game'].cat.categories))
    explanations = explain_recs(userid, gameplay_time, [r[0] for r in recs], model)
    recommendations = []
    for i, r in enumerate(recs):
        expln = [games[g] for g in explanations[i]]
        recommendations.append((games[r[0]], expln))
    return recommendations

def load(filename):
    # Chuck it all into a dataframe and a sparse matrix format!
    data = pd.read_csv(filename, names=['user', 'game', 'hours'])
    data['user'] = data['user'].astype('category')
    data['game'] = data['game'].astype('category')
    gameplay_time = coo_matrix((data['hours'].astype(np.float64),
                       (data['game'].cat.codes.copy(),
                        data['user'].cat.codes.copy())))
    return data, gameplay_time

def explain_recs(userid, user_items, itemids, model):
    explanations = []
    user_weights = None
    for itemid in itemids:
        total_score, top_contributions, user_weights = model.explain(userid, user_items, itemid, user_weights, N=4)
        explanations.append([t[0] for t in top_contributions])
        user_weights = user_weights
    return explanations
