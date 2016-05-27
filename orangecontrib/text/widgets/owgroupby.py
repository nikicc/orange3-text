from PyQt4 import QtGui
from itertools import chain

from PyQt4.QtGui import QApplication

from Orange.data import ContinuousVariable, DiscreteVariable, StringVariable, TimeVariable
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget
from Orange.widgets.data.owselectcolumns import VariablesListItemModel, VariablesListItemView
from orangecontrib.text.corpus import Corpus


class Types:
    CORPUS = 'Corpus'

class OWGroupBy(OWWidget):
    name = 'Group By'
    description = 'Group By ....'
    # icon = 'icons/BagOfWords.svg'
    priority = 10

    # Input/output
    inputs = [
        (Types.CORPUS, Corpus, 'set_data'),
    ]
    outputs = [
        (Types.CORPUS, Corpus)
    ]

    operator_names = {
        ContinuousVariable: ["equals", "is not",
                             "is below", "is at most",
                             "is greater than", "is at least",
                             "is between", "is outside",
                             "is defined"],
        DiscreteVariable: ["is", "is not", "is one of", "is defined"],
        StringVariable: ["equals", "is not",
                         "is before", "is equal or before",
                         "is after", "is equal or after",
                         "is between", "is outside", "contains",
                         "begins with", "ends with",
                         "is defined"]}
    operator_names[TimeVariable] = operator_names[ContinuousVariable]

    want_main_area = False

    # Settings
    autocommit = Setting(False)
    group_by_attrs = Setting([])
    unused_attrs = Setting([])

    def __init__(self):
        super().__init__()

        self.corpus = None

        fbox = gui.widgetBox(self.controlArea, orientation=0)

        # Group by attrs
        ubox = gui.widgetBox(fbox, "Group by", addSpace=True)
        self.group_by_attrs = VariablesListItemModel()
        self.group_by_attrs_view = VariablesListItemView()
        self.group_by_attrs_view.setModel(self.group_by_attrs)
        ubox.layout().addWidget(self.group_by_attrs_view)

        self.group_by_attrs.dataChanged.connect(self.update_feature_selection)
        self.group_by_attrs.rowsInserted.connect(self.update_feature_selection)
        self.group_by_attrs.rowsRemoved.connect(self.update_feature_selection)

        # Unused attrs
        ibox = gui.widgetBox(fbox, "Available features", addSpace=True)
        self.unused_attrs = VariablesListItemModel()
        self.unused_attrs_view = VariablesListItemView()
        self.unused_attrs_view.setModel(self.unused_attrs)
        ibox.layout().addWidget(self.unused_attrs_view)

        # Grouping conditions
        box = gui.vBox(self.controlArea, 'Group conditions', stretch=100)
        self.cond_list = QtGui.QTableWidget(box)
        box.layout().addWidget(self.cond_list)
        self.cond_list.setShowGrid(False)
        self.cond_list.setSelectionMode(QtGui.QTableWidget.NoSelection)
        self.cond_list.setColumnCount(3)
        self.cond_list.setRowCount(0)
        self.cond_list.verticalHeader().hide()
        self.cond_list.horizontalHeader().hide()
        self.cond_list.resizeColumnToContents(0)
        self.cond_list.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.cond_list.viewport().setBackgroundRole(QtGui.QPalette.Window)

        box2 = gui.hBox(box)
        self.add_button = gui.button(box2, self, "Add Condition",
                                     callback=self.add_row)
        self.add_all_button = gui.button(box2, self, "Add All Variables",
                                         callback=self.add_all)
        self.remove_all_button = gui.button(box2, self, "Remove All",
                                            callback=self.remove_all)
        gui.rubber(box2)

        gui.auto_commit(
                self.controlArea,
                self,
                'autocommit',
                'Commit',
                box=False
        )

    def set_data(self, data):
        self.corpus = data
        if data is not None:
            self.unused_attrs.extend(list(chain(data.domain.variables, data.domain.metas)))
        self.commit()

    def commit(self):
        self.apply()

    def apply(self):
        pass

    def update_feature_selection(self):
        pass

    def add_row(self, attr=None, condition_type=None, condition_value=None):
        model = self.cond_list.model()
        row = model.rowCount()
        model.insertRow(row)

        attr_combo = QtGui.QComboBox(
            minimumContentsLength=12,
            sizeAdjustPolicy=QtGui.QComboBox.AdjustToMinimumContentsLengthWithIcon)
        attr_combo.row = row
        for var in chain(self.corpus.domain.variables, self.corpus.domain.metas):
            attr_combo.addItem(*gui.attributeItem(var))
        attr_combo.setCurrentIndex(attr or 0)
        self.cond_list.setCellWidget(row, 0, attr_combo)

        self.remove_all_button.setDisabled(False)
        self.set_new_operators(attr_combo, attr is not None,
                               condition_type, condition_value)
        attr_combo.currentIndexChanged.connect(
            lambda _: self.set_new_operators(attr_combo, False))

        self.cond_list.resizeRowToContents(row)

    def set_new_operators(self, attr_combo, adding_all,
                              selected_index=None, selected_values=None):
        oper_combo = QtGui.QComboBox()
        oper_combo.row = attr_combo.row
        oper_combo.attr_combo = attr_combo
        var = self.corpus.domain[attr_combo.currentText()]
        oper_combo.addItems(self.operator_names[type(var)])
        oper_combo.setCurrentIndex(selected_index or 0)
        self.set_new_values(oper_combo, adding_all, selected_values)
        self.cond_list.setCellWidget(oper_combo.row, 1, oper_combo)
        oper_combo.currentIndexChanged.connect(
            lambda _: self.set_new_values(oper_combo, False))


    def add_all(self):
            pass

    def remove_all(self):
        pass

if __name__ == '__main__':
    app = QApplication([])
    widget = OWGroupBy()
    widget.show()
    corpus = Corpus.from_file('bookexcerpts')
    widget.set_data(corpus)
    app.exec()
