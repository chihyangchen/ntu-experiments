# Machine Learning Model
import xgboost as xgb
import catboost as cb

# Predicter
class Predictor():

    def __init__(self, lte_cls=None, nr_cls=None, lte_fst=None, nr_fst=None, set_up=None, rlf=None):
        
        self.model_names = []
        self.file_names = []
        self.models = {}
        
        for name, file in zip(['lte_cls', 'nr_cls', 'lte_fst', 'nr_fst', 'set_up', 'rlf'], [lte_cls, nr_cls, lte_fst, nr_fst, set_up, rlf]):
            if file is None:
                continue
            self.model_names.append(name)
            self.file_names.append(file)
            # XGB Model 
            if 'xgb' in file:
                self.models[name] = xgb.Booster()
                self.models[name].load_model(file)
            # Catboost Model
            elif 'cb' in file:
                if 'cls' in file:
                    self.models[name] = cb.CatBoostClassifier()
                    self.models[name].load_model(file)
                elif 'fcst' in file:
                    self.models[name] = cb.CatBoostRegressor()
                    self.models[name].load_model(file)
        
    def foward(self, x_in):
        
        out = {}
        for (name, model), file in zip(self.models.items(), self.file_names):
            if file is None:
                continue
            # XGB Model
            if 'xgb' in file:
                x_in_D = xgb.DMatrix(x_in.reshape(1,-1))
                out[name] = model.predict(x_in_D)[0]
            # Catboost Model
            elif 'cb' in file:
                if 'cls' in file: # Classification
                    out[name] = model.predict_proba(x_in)[1]
                elif 'fcst' in file: # Regression
                    out[name] = model.predict(x_in)
        
        return out