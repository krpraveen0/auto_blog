```yaml
title: Building a UPI-Like Payment Flow with Java and Spring Boot: A Beginner's Guide
seo_description: Learn how to build a simple UPI-style payment flow using Java and Spring Boot with practical Indian examples.
suggested_tags:
  - Java
  - Spring Boot
  - UPI
  - Payment Gateway
  - IndianTech
canonical_url: ""
author: Praveen
```

# Building a UPI-Like Payment Flow with Java and Spring Boot: A Beginner's Guide

### TL;DR

- Understand the basics of UPI payment flow with Indian context.
- Build a simple Spring Boot REST API to create and verify payment orders.
- Implement mini projects simulating UPI transactions and order creation.
- Deep dive into key concepts: Virtual Payment Address (VPA), transaction routing, and payment verification.
- Troubleshoot common issues when integrating payment flows.
- Follow Praveen for more real-world build guides.

---

## Context: UPI and Payments in India

India’s Unified Payments Interface (UPI) has revolutionized how millions transact daily—from booking IRCTC train tickets, paying for cricket match tickets, to shopping using Rupay cards. UPI enables instant, real-time money transfers via Virtual Payment Addresses (VPAs) linked to bank accounts, all authenticated by a secure UPI PIN. Behind the scenes, the National Payments Corporation of India (NPCI) routes and validates each transaction quickly and reliably.

Imagine building your own simplified version of this payment flow using Java and Spring Boot, the popular framework in India’s tech ecosystem. This guide will walk you through creating a payment API that mimics UPI’s core steps, focusing on Indian payment scenarios, like Mumbai-based users sending money or paying for local services.

---

## Mini Project 1: Create a Simple UPI Order API

### GOAL

Build a Spring Boot API to create a payment order simulating UPI transaction requests.

### PREREQS

- Java 17+
- Spring Boot (Spring Web starter)
- Maven or Gradle
- Basic knowledge of REST APIs

### STEP-BY-STEP

1. **Setup Spring Boot project** with Spring Web dependency.
2. **Create a PaymentOrder model** to hold order details (amount, currency, VPA).
3. **Create a PaymentService** to generate a mock order ID and store order info in memory.
4. **Expose a REST endpoint** `/createOrder` accepting amount, currency (INR), and VPA.
5. **Return order details** including a unique order ID and status.

### CODE (Java + Spring Boot)

```java
@RestController
@RequestMapping("/upi")
public class PaymentController {

    private Map<String, PaymentOrder> orders = new ConcurrentHashMap<>();

    @PostMapping("/createOrder")
    public ResponseEntity<PaymentOrder> createOrder(@RequestBody PaymentRequest request) {
        // Validate inputs (amount > 0, VPA format)
        if(request.getAmount() <= 0 || !request.getVpa().contains("@")) {
            return ResponseEntity.badRequest().build();
        }
        String orderId = UUID.randomUUID().toString();
        PaymentOrder order = new PaymentOrder(orderId, request.getAmount(), "INR", request.getVpa(), "CREATED");
        orders.put(orderId, order);
        return ResponseEntity.ok(order);
    }

    // Simple DTOs
    static class PaymentRequest {
        private double amount;
        private String vpa;
        // getters and setters
    }

    static class PaymentOrder {
        private String orderId;
        private double amount;
        private String currency;
        private String vpa;
        private String status;
        // constructor, getters
    }
}
```

### SAMPLE INPUT/OUTPUT

**Request:**  
POST `/upi/createOrder`  
```json
{
  "amount": 1500,
  "vpa": "praveen@okaxis"
}
```

**Response:**  
```json
{
  "orderId": "3f47c6e0-9b3a-4e8e-8e9c-2e3f2a4f5b2d",
  "amount": 1500,
  "currency": "INR",
  "vpa": "praveen@okaxis",
  "status": "CREATED"
}
```

### What could go wrong?

- Invalid VPA format (missing '@')
- Negative or zero amount
- Duplicate order IDs if UUID generation fails (very rare)
- Missing required request fields

---

## Mini Project 2: Simulate Payment Verification Flow

### GOAL

Verify a mock payment by updating order status after "payment" confirmation.

### PREREQS

- Completed Mini Project 1
- Basic REST knowledge

### STEP-BY-STEP

1. Add an endpoint `/upi/verifyPayment` accepting an order ID and a mock payment status.
2. Check if the order exists and update status to `SUCCESS` or `FAILED`.
3. Return updated order details.

### CODE

```java
@PostMapping("/verifyPayment")
public ResponseEntity<PaymentOrder> verifyPayment(@RequestParam String orderId, @RequestParam String status) {
    PaymentOrder order = orders.get(orderId);
    if (order == null) {
        return ResponseEntity.notFound().build();
    }
    if (!status.equalsIgnoreCase("SUCCESS") && !status.equalsIgnoreCase("FAILED")) {
        return ResponseEntity.badRequest().build();
    }
    order.setStatus(status.toUpperCase());
    return ResponseEntity.ok(order);
}
```

### SAMPLE INPUT/OUTPUT

**Request:**  
POST `/upi/verifyPayment?orderId=3f47c6e0-9b3a-4e8e-8e9c-2e3f2a4f5b2d&status=SUCCESS`

**Response:**  
```json
{
  "orderId": "3f47c6e0-9b3a-4e8e-8e9c-2e3f2a4f5b2d",
  "amount": 1500,
  "currency": "INR",
  "vpa": "praveen@okaxis",
  "status": "SUCCESS"
}
```

### What could go wrong?

- Verifying non-existing order
- Invalid status input
- Race condition if multiple verifications occur simultaneously

---

## Mini Project 3: Integrate with Razorpay (Optional)

### GOAL

Integrate Razorpay payment gateway in Spring Boot for real payments.

### PREREQS

- Razorpay account (sandbox keys)
- Spring Boot knowledge
- Maven dependencies for Razorpay SDK

### STEP-BY-STEP

1. Add Razorpay SDK dependency in `pom.xml`.
2. Configure Razorpay client with API keys (use environment variables).
3. Create order via Razorpay API.
4. Expose endpoints to create and verify payment orders.
5. Handle webhook for payment confirmation.

### CODE SNIPPET (Service Layer)

```java
@Service
public class RazorpayPaymentService {

    private RazorpayClient client;

    @Value("${razorpay.key}")
    private String key;

    @Value("${razorpay.secret}")
    private String secret;

    @PostConstruct
    public void init() throws RazorpayException {
        client = new RazorpayClient(key, secret);
    }

    public Order createOrder(double amount) throws RazorpayException {
        JSONObject options = new JSONObject();
        options.put("amount", (int)(amount * 100)); // in paise
        options.put("currency", "INR");
        options.put("payment_capture", 1);
        return client.Orders.create(options);
    }
}
```

### What could go wrong?

- Incorrect API keys or missing environment variables
- Amount mismatch (INR to paise conversion errors)
- Network issues calling Razorpay APIs
- Handling asynchronous payment confirmation properly

---

## Deep Dive: How UPI Payment Flow Works Behind the Scenes

UPI operates on a **real-time payment system** where:

- The user initiates a payment by entering a **Virtual Payment Address (VPA)**, e.g., `praveen@okaxis`.
- The UPI app sends the payment request to the **Network Provider Service Provider (NPSP)**.
- The NPSP routes the request to **NPCI**, which acts as the central switch.
- NPCI validates the transaction and forwards it to the **remitter’s bank**.
- The remitter’s bank authenticates the transaction (usually by UPI PIN) and debits the amount.
- NPCI then instructs the **beneficiary’s bank** to credit the beneficiary’s account.
- Confirmation is sent back through the same channels to the user app.

This entire flow happens in **seconds**, enabling instant transfer.

The key components to simulate in a UPI-like API:

- **Order creation:** mimics initiating a payment request.
- **Transaction routing:** handled by NPCI and banks, here simplified.
- **Verification:** confirmation of successful debit and credit.

Understanding this helps when designing your own payment flows and APIs, especially regarding security and asynchronous processing.

---

## Troubleshooting & FAQ

**Q1: What if my payment order creation API returns 400?**  
Check that the amount is positive and VPA format includes '@'. Validate all inputs carefully.

**Q2: How do I secure my payment API?**  
Use HTTPS, validate input data, and secure sensitive keys via environment variables. Implement authentication for your APIs.

**Q3: Can I test with real UPI transactions?**  
Use sandbox/test environments provided by payment gateways or NPCI-approved partners. Never expose real credentials in development.

**Q4: What if payment verification fails?**  
Verify that order IDs exist and the payment status matches expected values. Check logs and network calls to payment gateway.

**Q5: How to handle concurrency in payment updates?**  
Use thread-safe data structures or database transactions to prevent race conditions.

---

## Follow Praveen for More Real-World Build Guides

Building a UPI-like payment flow is a practical way to understand India’s payment infrastructure and Java Spring Boot development. Try these mini projects, experiment with real payment gateways, and deepen your knowledge with each step. Follow me, Praveen, for more hands-on guides that bridge coding with Indian tech realities.