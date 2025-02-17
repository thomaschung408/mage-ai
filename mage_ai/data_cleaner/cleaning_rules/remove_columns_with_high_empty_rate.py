from mage_ai.data_cleaner.cleaning_rules.base import BaseRule
from mage_ai.data_cleaner.transformer_actions.constants import (
    ActionType,
    Axis,
)


class RemoveColumnsWithHighEmptyRate(BaseRule):
    MISSING_RATE_THRESHOLD = 0.8

    def evaluate(self):
        columns_with_missing_values = []
        columns_with_no_values = []
        for c in self.df_columns:
            if self.statistics.get(f'{c}/count') == 0:
                columns_with_no_values.append(c)
            elif f'{c}/null_value_rate' in self.statistics:
                null_value_rate = self.statistics[f'{c}/null_value_rate']
                if null_value_rate >= self.MISSING_RATE_THRESHOLD:
                    columns_with_missing_values.append(c)

        suggestions = []
        if len(columns_with_no_values) > 0:
            suggestions.append(self._build_transformer_action_suggestion(
                'Remove columns with no values',
                f'The following columns have no values: {columns_with_no_values}.'\
                ' Removing them may increase your data quality.',
                ActionType.REMOVE,
                action_arguments=columns_with_no_values,
                axis=Axis.COLUMN,
            ))
        if len(columns_with_missing_values) > 0:
            suggestions.append(self._build_transformer_action_suggestion(
                'Remove columns with high empty rate',
                f'The following columns have high empty rate: {columns_with_missing_values}.'\
                ' Removing them may increase your data quality.',
                ActionType.REMOVE,
                action_arguments=columns_with_missing_values,
                axis=Axis.COLUMN,
            ))
        return suggestions
