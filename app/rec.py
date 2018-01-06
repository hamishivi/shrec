import pandas as pd
import numpy as np
import implicit
from scipy.sparse import coo_matrix

def get_rec(username, df, gameplay_time):
    '''
    get a recommendation for a user given a username (steam id), a numpy dataframe with a list of users and games, and a sparse matrix of games by users, which each cell has the amount of hours played.
    returns a list of (game, explanation) tuples
    '''
    # create a model
    model = implicit.als.AlternatingLeastSquares()
    try:
        # get the user_id mapping from the sparse matrix
        user_id = df['user'].cat.categories.tolist().index(int(username))
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
    recs = model.recommend(user_id, user_plays, N=len(df['game'].cat.categories))
    # explain each recommendation
    explanations = explain_recs(user_id, gameplay_time, [rec for rec, *_ in recs], model, 4)
    # convert from the matrix ids to the game ids as per steam
    recommendations = [(games[rec], [games[g] for g in expln]) for (rec, *_), expln in zip(recs, explanations)]
    return recommendations


def load(filename):
    '''
    Loads a file and chucks it all into a dataframe and a sparse matrix
    '''
    data = pd.read_csv(filename, names=['user', 'game', 'hours'])
    data['user'] = data['user'].astype('category')
    data['game'] = data['game'].astype('category')
    gameplay_time = coo_matrix((data['hours'].astype(np.float64),
                       (data['game'].cat.codes.copy(),
                        data['user'].cat.codes.copy())))
    return data, gameplay_time


def explain_recs(user_id, user_items, item_ids, model, n):
    '''
    This takes in a user_id (based from the matrix), a sparse matrix (not csr) to generate
    the explanations from, a list of items/recommendations to explain, and the model itself.
    It then returns a list of n games per explanation.
    '''
    user_weights = None
    for item_id in item_ids:
        # N is the number of items you put in the explanation.
        # User weights can be reused between calls to speed it up
        _, top_contributions, user_weights = model.explain(user_id, user_items, item_id, user_weights, N=n)
        yield [t for t, *_ in top_contributions]
