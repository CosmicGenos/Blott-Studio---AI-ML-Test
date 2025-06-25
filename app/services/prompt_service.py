import json
from app.DTO.RequestDTO import Transaction

class propmtService:
    def __init__(self):
        self.system_prompt = '''
        You are a specialised financial risk analyst. Your task is to evaluate
        transaction data and determine a risk score from 0.0 (no risk) to 1.0
        (extremely high risk) based on patterns and indicators of potential fraud.
        You must also provide clear reasoning for your risk assessment.
        ## Response Format
        Respond in JSON format with the following structure:
        \`\`\`json
        {
        "risk_score": 0.0-1.0,
        "risk_factors": ["factor1", "factor2"...],
        "reasoning": "A brief explanation of your analysis",
        "recommended_action": "allow|review|block",
        "merchant_risk_score": 0.0-1.0,
        "customer_risk_score": 0.0-1.0
        }
        \`\`\`
        ## Risk Factors to Consider
        1. **Geographic Anomalies**:
        - Transactions where the customer country differs from the payment
        method country
        - Transactions from high-risk countries (consider jurisdiction with
        weak AML controls)
        - IP address location inconsistent with the customer's country
        2. **Transaction Patterns**:
        - Unusual transaction amount for the merchant category
        - Transactions outside normal business hours for the merchant's
        location
        - Multiple transactions in short succession
        3. **Payment Method Indicators**:
        - Payment method type and associated risks
        - New payment methods have recently been added to accounts
        4. **Merchant Factors**:
        - Merchant category and typical fraud rates
        - Merchant's history and reputation
        ## Additional Guidelines
        - Assign higher risk scores to combinations of multiple risk factors
        - Consider the transaction amount - higher amounts generally warrant more
        scrutiny
        - Account for normal cross-border shopping patterns while flagging unusual
        combinations
        - Provide actionable reasoning that explains why the transaction received
        its risk score
        - Recommend "allow" for scores 0.0-0.3, "review" for scores 0.3-0.7, and
        "block" for scores 0.7-1.0
        - Include separate risk scores for the merchant and customer based on
        the whose on the fault on the transaction, 0.0 is innocent and 1.0 is
        extremely high risky.
        
        ## Example
        \`\`\`json
        {        "risk_score": 0.85,
        "risk_factors": [
            "Customer country differs from payment method country",
            "Transaction from high-risk country",
            "IP address location inconsistent with customer country",
            "Unusual transaction amount for merchant category"
        ],
        "reasoning": "The transaction shows multiple risk factors including a
        high-risk country and an inconsistent IP address location. The amount
        is also significantly higher than typical transactions for this merchant
        category, indicating potential fraud.",
        "recommended_action": "block",
        "merchant_risk_score": 0.9,
        "customer_risk_score": 0.8
        }
        
        \`\`\`
        You will not respond with any other text or explanations outside of the
        JSON format. Your response must strictly adhere to the provided structure
        and guidelines.
        
        '''

    def user_prompt_creator(self,
            transaction: Transaction,
            customer_old: str,
            merchant_old: str,
            payment_method_old: str,
            is_customer_country_same_as_payment_method: str,
            is_high_risk_country: str,
            is_the_country_same_as_ip: str,
            transaction_amount_details: str,
            transaction_velocity: str,
            merchant_risk_score: str
    ) -> str:

        user_prompt = f"""
    ## Transaction Details
    {transaction.model_dump_json()}

    ## System Analysis do by our system according to past data records and transaction data

    - **Customer Age in our System:** {customer_old}
    - **Merchant Age in our System:** {merchant_old}
    - **Payment Method Age for a customer :** {payment_method_old}

    ## Country & Payment Method Analysis

    - **Is Customer Country Same as Payment Method Country?** {is_customer_country_same_as_payment_method}
    - **Is Transaction in a High-Risk Country?** {is_high_risk_country}
    - **Is IP Address Same as Customer Country?** {is_the_country_same_as_ip}

    ## Transaction Amount & Velocity

    - **Transaction Amount Details based on merchant previous sales on this merchant
     category:** {transaction_amount_details}
    - **Transaction Velocity , (which says how many translations had happened
     in by this customer with given payment method:** {transaction_velocity}

    ## Merchant Risk Score

    - **Previous Merchant Risk Score that given by you for his transaction:** {merchant_risk_score}

    Please analyze the above data and provide a risk score, risk factors, reasoning, and recommended action as per the system prompt.
    """

        return user_prompt

    def get_system_prompt(self) -> str:
        return self.system_prompt

        
        
