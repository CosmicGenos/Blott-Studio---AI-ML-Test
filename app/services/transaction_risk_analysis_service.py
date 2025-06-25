from app.services.geographic_analysis_service import GeographicAnalysis
from app.services.record_history_analysis_service import RecordAvailability
from app.services.transaction_pattern_analysis_service import PatternAnalysis
from app.services.prompt_service import propmtService
from app.services.LLM_service import LLMService
from app.DTO.RequestDTO import Transaction
from app.DTO.ResponseDTO import RiskAssessmentDTO
from app.services.data_update_service import DataIntegration




class TransactionRiskAnalysis:
    def __init__(self,
                 geographic_analysis: GeographicAnalysis,
                 record_availability: RecordAvailability,
                 pattern_analysis: PatternAnalysis,
                 prompt_service: propmtService,
                 llm_service: LLMService,
                 dataIntegration_service: DataIntegration
                 ):
        self.geographic_analysis = geographic_analysis
        self.record_availability = record_availability
        self.pattern_analysis = pattern_analysis
        self.prompt_service = prompt_service
        self.llm_service = llm_service
        self.dataIntegration_service = dataIntegration_service

    async def analyze_the_risk(self, transaction: Transaction) -> RiskAssessmentDTO:

        # step 1: check availability of customer and merchant records

        is_customer_new, customer_status = await self.record_availability.check_customer_history(
            transaction.customer.id)

        is_merchant_new, merchant_status = await self.record_availability.check_merchant_history(
            transaction.merchant.id)

        is_payment_method_new, payment_method_status = await self.record_availability.check_payment_method(
            transaction.customer.id,
            transaction.payment_method.type,
            transaction.payment_method.last_four,
            transaction.payment_method.country_of_issue
        )

        is_merchant_is_good_in_history = "he is a new merchant, we don't have history to analyze."
        if not is_merchant_new:
            result = await self.record_availability.get_merchant_risk_and_transaction_count(
                transaction.merchant.id)
            if result is None:
                is_merchant_is_good_in_history = "it is a new category for this merchant, we don't have history to analyze."
            else:
                merchant_individual_risk_score, transaction_count_involved = result
                is_merchant_is_good_in_history = (
                    f"according to past data records, this merchant has a risk score of "
                    f"{merchant_individual_risk_score} and has processed {transaction_count_involved} ."
                )

        # step 2: analyze transaction patterns

        Transcation_velocity = "Since this is a new customer, we don't have transaction history to analyze velocity."
        if not is_customer_new:
            customer_velocity = await self.pattern_analysis.transaction_velocity_analysis(
                transaction.customer.id,
                transaction.payment_method.type,
                transaction.payment_method.last_four,
                transaction.payment_method.country_of_issue
            )
            Transcation_velocity = (
                f"had this transactions on past year ,with these time periods: {customer_velocity}"
            )

        merchant_category_stats = "Since this is a new merchant, we don't have category statistics to analyze."
        if not is_merchant_new:
            result = await self.pattern_analysis.analyze_merchant_sells_for_category(
                transaction.merchant.id,
                transaction.merchant.category
            )
            if result is None:
                merchant_category_stats = "it is a new category for this merchant, we don't have history to analyze."
            else:
                mean, variance = result
                merchant_category_stats = (
                    f"according to past data records, for this merchant category with this given merchant, "
                    f"we wind average price of {mean} and variability (standard deviation) of {variance}."
                )


        # step 3: geographic analysis

        customer_country = transaction.customer.country.strip().upper()
        payment_method_country = transaction.payment_method.country_of_issue.strip().upper()

        customer_country_analysis, is_same_country = await self.geographic_analysis.Is_the_country_same_as_payment_method(
            customer_country, payment_method_country
        )
        is_high_risk_country, is_high_risk = await self.geographic_analysis.is_high_risk_country(customer_country)

        is_country_same_as_ip, is_same_as_ip = await self.geographic_analysis.Is_the_country_same_as_payment_method(
            customer_country, transaction.customer.ip_address
        )


        # step 4: create user prompt

        user_prompt = self.prompt_service.user_prompt_creator(
            transaction=transaction,
            customer_old=customer_status,
            merchant_old=merchant_status,
            payment_method_old=payment_method_status,
            is_customer_country_same_as_payment_method=customer_country_analysis,
            is_high_risk_country=is_high_risk_country,
            is_the_country_same_as_ip=is_country_same_as_ip,
            transaction_amount_details=merchant_category_stats,
            transaction_velocity=Transcation_velocity,
            merchant_risk_score=is_merchant_is_good_in_history
        )
        print("\n===== USER PROMPT =====\n", user_prompt, "\n========================\n")

        # step 5: get system prompt
        system_prompt = self.prompt_service.get_system_prompt()


        # step 6: get risk assessment from LLM
        llm_response = await self.llm_service.get_risk_assessment(
            user_prompt=user_prompt,
            system_prompt=system_prompt
        )

        # step 7: update the data integration service with the transaction data

        customer_primary_key = await self.dataIntegration_service.save_customer_data(
            customer_id=transaction.customer.id,
            is_new_customer=is_customer_new,
            individual_risk_score=llm_response.customer_risk_score)

        merchant_primary_key = await self.dataIntegration_service.save_merchant_data(
            merchant_id=transaction.merchant.id,
            is_new_merchant=is_merchant_new,
            individual_risk_score=llm_response.merchant_risk_score,
            merchant_name=transaction.merchant.name)

        payment_method_primary_key = await self.dataIntegration_service.save_payment_method(
            customer_no=customer_primary_key,
            is_new_payment=is_payment_method_new,
            type=transaction.payment_method.type,
            last_four=transaction.payment_method.last_four,
            country_of_issue=transaction.payment_method.country_of_issue
        )

        customer_location_primary_key = await self.dataIntegration_service.save_customer_location(
            customer_no=customer_primary_key,
            location=transaction.customer.country
        )

        customer_ip_address_primary_key = await self.dataIntegration_service.save_customer_ip_address(
            customer_no=customer_primary_key,
            ip_address=transaction.customer.ip_address
        )

        merchant_category_primary_key = await self.dataIntegration_service.save_merchant_category(
            merchant_no=merchant_primary_key,
            category_name=transaction.merchant.category
        )



        transaction_primary_key = await self.dataIntegration_service.save_transaction(
            transaction_id=transaction.transaction_id,
            customer_no=customer_primary_key,
            merchant_no=merchant_primary_key,
            customer_payment_method_id=payment_method_primary_key,
            amount=transaction.amount,
            currency=transaction.currency,
            risk_score= llm_response.risk_score,
            merchant_category_id=merchant_category_primary_key,

        )

        risk_score_primary_key = await self.dataIntegration_service.save_risk_score(
            customer_no=customer_primary_key,
            merchant_no=merchant_primary_key,
            transaction_no= transaction_primary_key,
            llm_analysis=llm_response.reasoning,
            risk_factors= llm_response.risk_factors,
            score=llm_response.risk_score,
            alert_type= llm_response.recommended_action,
            recommendedAction= llm_response.recommended_action.value
        )


        _ = await self.dataIntegration_service.save_notification(
            transaction_no=transaction_primary_key,
            customer_no=customer_primary_key,
            merchant_no= merchant_primary_key,
            risk_score_id=risk_score_primary_key,
            merchant_category_id=merchant_category_primary_key,
            customer_payment_method_id=payment_method_primary_key,
            customer_location_id=customer_location_primary_key,
            customer_ip_address_id= customer_ip_address_primary_key
        )

        await self.dataIntegration_service.commit_all()


        # step 7: return the risk assessment
        return llm_response






