# Copyright 2012-2013, University of Amsterdam. This program is free software:
# you can redistribute it and/or modify it under the terms of the GNU Lesser 
# General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License 
# for more details.
# 
# You should have received a copy of the GNU Lesser General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from core import LinksProcessor
from util import ModelStore

import warnings

from collections import defaultdict

class LearningProcessor(LinksProcessor):
    def __init__(self, model_dir):
        self.modelStore = ModelStore(model_dir)
        self.history = defaultdict(list)
        self.context_history = defaultdict(list)

    def predict(self, classifier, testfeatures):
        print("Start predicting of %d instances with %d features."
              % (len(testfeatures), len(testfeatures[0])))
        predict = classifier.predict_proba(testfeatures)
        print("Done predicting of %d instances." % len(predict))

        return predict    

    def check_model(self, model, description, features, settings):
        if "language" in description:
            assert settings["langcode"] == description["language"], \
                "Language of model and data do not match."
        
        if "features" in description:
            missing_features = set(description["features"]) - set(features)
            if(len(missing_features)):
                warn = RuntimeWarning("Missing %d features for model %s: %s "
                                      % (len(missing_features), 
                                         description["name"],
                                         ", ".join(missing_features)))
                
                if "missing" in settings:
                    warnings.warn(warn)
                else:
                    raise warn

            features = sorted(description["features"])
        
        if model.n_features_ != len(features):
            raise ValueError("Number of features of the model must "
                             "match the input. Model n_features is %s and "
                             "input n_features is %s."
                             % (model.n_features_, len(features)))

        return features

    def process(self, links, text, settings):
        if not "learning" in settings or len(links) == 0:
            return (links, text, settings)
        
        modelname = settings["learning"]
        (model, description) = self.modelStore.load_model(modelname)
        print("Loaded classifier from %s" % description["source"])

        features = sorted(links[0]["features"].keys())        
        features = self.check_model(model, description, features, settings)

        testfeatures = []
        for link in links:
            linkfeatures = []
            for feature in features:
                if feature in link["features"]:
                    linkfeatures.append(link["features"][feature])
                else:
                    linkfeatures.append(None)
            testfeatures.append(linkfeatures)

        scores = self.predict(model, testfeatures)
        for link, score in zip(links, scores):
            link["learning_probability"] = score[1]

        return (links, text, settings)

    def postprocess(self, links, text, settings):
        if "save" in settings:
            history = self.history[settings["request_id"]]

        for link in links:
            if "context" in settings:
                link["context"] = settings["context"]
            if "save" in settings:
                history.append(link if "features" in settings else link.copy())
            if "learning" in settings and "features" not in settings:
                del link["features"]

        if "save" in settings and "context" in settings:
            context_history = self.context_history[settings["context"]]
            context_history.append(settings["request_id"])

        return (links, text, settings)

    def inspect(self):
        history = {"history": self.history,
                   "context_history": self.context_history}
        return {self.__class__.__name__: history}

    def feedback(self, request_id, context, feedback):
        if request_id != None:
            request_ids = [request_id]
            if context and request_id not in self.context_history[context]:
                raise ValueError("Request id %s not found in context %s." %
                                 (request_id, context))
        else:
            request_ids = self.context_history[context]
            if len(request_ids) == 0:
                raise ValueError("No requests found for context %s." % context)
        
        print("Received feedback for request_id %s in context %s: %s." %
                              (request_id, context, feedback))
                              
        def process_feedback(link, feedback):
            link["feedback"] = feedback
            print feedback, link["title"]

        for feedback_request_id in request_ids:
            if feedback_request_id not in self.history:
                raise ValueError("Request id %s not found in history." %
                                 request_id)
            for link in self.history[feedback_request_id]:
                for feedback_type in feedback.keys():
                    if feedback_type == "default": continue
                    if link["title"] in feedback.getlist(feedback_type):
                        process_feedback(link, feedback_type)
                        break
                else:
                    if "default" in feedback:
                        process_feedback(link, feedback["default"])