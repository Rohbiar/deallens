-- Every unverified record, including machine-supported scalar records.
SELECT document_id, field_name, document_layer, status, page
FROM review_queue ORDER BY run_id, document_id, field_name;

-- Conflicts across filing and underlying agreements.
SELECT run_id, document_id, field_name, record_json
FROM comparisons WHERE classification = 'conflict';

-- Compare hedge costs without summing annual coupons and PV sensitivities.
SELECT document_id, scenario_id, strategy, currency, net_cost
FROM scenarios WHERE scenario_id IN ('rates_up_25', 'failure_rates_down_25')
ORDER BY run_id, document_id, scenario_id, strategy;

-- Recover the original normalized page for a stored record.
SELECT f.document_id, f.field_name, f.page, p.text
FROM fields AS f JOIN pages AS p
ON p.run_id=f.run_id AND p.document_id=f.document_id AND p.page=f.page
WHERE f.status='supported';
