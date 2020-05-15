from calim import *
import pickle



filename = 'C:\\Users\\Gabriel\\Documents\\Python Scripts\\CalciumImaging\\\
ClassExperiments\\raw\\191106_s1r2_Results.csv'

project = Project(name="Meclofenamate in ZG")

exp_data = pd.read_csv(filename, index_col=0)
experiment = Recording(file_id="test.csv", dt=0.1, raw_data=exp_data,
                       animal=999, genotype="wt", birthdate="2019-05-01")
el = experiment.cells["Mean3"].find_events(cutoff=0.05)
experiment.cells["Mean3"].set_events(el)
c1 = {"start": 2000, "end": 4100, "meclofenamate": 0, "potassium": 4,
      "angiotensin": 500}
c2 = {"start": 4101, "end": 8010, "meclofenamate": 10, "potassium": 4,
      "angiotensin": 500}
c3 = {"start": 8011, "end": 10440, "meclofenamate": 0, "potassium": 4,
      "angiotensin": 500}
experiment.add_condition(**c1)
experiment.add_condition(**c2)
experiment.add_condition(**c3)


project.append(experiment)

experiment = Recording(file_id="test_2.csv", dt=0.1, raw_data=exp_data,
                       animal=111, genotype="wt", birthdate="2019-06-01")
el = experiment.cells["Mean3"].find_events(cutoff=0.05)
experiment.cells["Mean3"].set_events(el)
c1 = {"start": 2000, "end": 4100, "meclofenamate": 0, "potassium": 4,
      "angiotensin": 500}
c2 = {"start": 4101, "end": 8010, "meclofenamate": 10, "potassium": 4,
      "angiotensin": 500}
c3 = {"start": 8011, "end": 10440, "meclofenamate": 0, "potassium": 4,
      "angiotensin": 500}
experiment.add_condition(**c1)
experiment.add_condition(**c2)
experiment.add_condition(**c3)


project.append(experiment)


pickle.dump(project, open("save.pkl", "wb" ) )