"""Builds a small but realistic Spring + MyBatis + JS project for tests/demos."""

from __future__ import annotations

from pathlib import Path

FILES = {
    "pom.xml": """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.acme</groupId><artifactId>shop</artifactId><version>1.2.0</version>
  <packaging>war</packaging><name>Acme Shop</name>
  <properties><java.version>11</java.version></properties>
  <dependencies>
    <dependency><groupId>org.springframework</groupId><artifactId>spring-webmvc</artifactId><version>5.3.0</version></dependency>
    <dependency><groupId>org.mybatis</groupId><artifactId>mybatis</artifactId><version>3.5.9</version></dependency>
    <dependency><groupId>junit</groupId><artifactId>junit</artifactId><scope>test</scope></dependency>
  </dependencies>
</project>
""",
    "src/main/java/com/acme/web/UserController.java": """package com.acme.web;

import com.acme.model.User;
import com.acme.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/** REST endpoints for user management. */
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    /** Load one user by id. */
    @GetMapping("/{id}")
    public User get(@PathVariable("id") Long id) {
        return userService.find(id);
    }

    @PostMapping
    public User create(@RequestBody User user) {
        return userService.save(user);
    }
}
""",
    "src/main/java/com/acme/service/UserService.java": """package com.acme.service;

import com.acme.model.User;

public interface UserService {
    User find(Long id);
    User save(User user);
}
""",
    "src/main/java/com/acme/service/UserServiceImpl.java": """package com.acme.service;

import com.acme.dao.UserMapper;
import com.acme.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserMapper userMapper;

    @Value("${app.default.role}")
    private String defaultRole;

    @Override
    public User find(Long id) { return userMapper.selectById(id); }

    @Override
    @Transactional
    public User save(User user) {
        if (user.getRole() == null) { user.setRole(defaultRole); }
        userMapper.insert(user);
        return user;
    }
}
""",
    "src/main/java/com/acme/dao/UserMapper.java": """package com.acme.dao;

import com.acme.model.User;

public interface UserMapper {
    User selectById(Long id);
    int insert(User user);
}
""",
    "src/main/java/com/acme/model/User.java": """package com.acme.model;

import javax.persistence.Entity;
import javax.persistence.Table;

@Entity
@Table(name = "app_user")
public class User {
    private Long id;
    private String name;
    private String role;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
}
""",
    "src/main/java/com/acme/util/Unused.java": """package com.acme.util;

public final class Unused {
    private Unused() {}
    public static String hello() { return "class Fake { }"; } // { unbalanced in comment
}
""",
    "src/main/resources/mapper/UserMapper.xml": """<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.acme.dao.UserMapper">
  <select id="selectById" parameterType="long" resultType="com.acme.model.User">
    SELECT id, name, role FROM app_user WHERE id = #{id}
  </select>
  <insert id="insert" parameterType="com.acme.model.User">
    INSERT INTO app_user (name, role) VALUES (#{name}, #{role})
  </insert>
</mapper>
""",
    "src/main/resources/applicationContext.xml": """<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:context="http://www.springframework.org/schema/context">
  <context:component-scan base-package="com.acme"/>
  <context:property-placeholder location="classpath:app.properties"/>
  <bean id="userService" class="com.acme.service.UserServiceImpl"/>
</beans>
""",
    "src/main/resources/app.properties": """# application settings
app.default.role=viewer
db.url=jdbc:mysql://localhost:3306/shop?user=root&password=hunter2
db.password=hunter2
greeting=\\u0b95\\u0bc1\\u0bb2\\u0bbf\\u0bb0\\u0bcd
long.value=part one \\
    part two
""",
    "src/main/webapp/WEB-INF/web.xml": """<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://java.sun.com/xml/ns/javaee" version="3.0">
  <servlet><servlet-name>legacy</servlet-name><servlet-class>com.acme.web.LegacyServlet</servlet-class></servlet>
  <servlet-mapping><servlet-name>legacy</servlet-name><url-pattern>/legacy/*</url-pattern></servlet-mapping>
  <context-param><param-name>dbPassword</param-name><param-value>s3cret</param-value></context-param>
</web-app>
""",
    "src/main/webapp/js/users.js": """/**
 * User screen logic.
 */
function loadUser(id) {
  $.get('/shop/api/users/' + id, function (u) { render(u); });
}
var saveUser = function (user) {
  $.ajax({ url: '/shop/api/users', type: 'POST', data: user });
};
const render = (u) => { console.log("function fake() {}"); };
""",
    "src/main/webapp/js/jquery-3.6.0.min.js": "/*! jQuery v3.6.0 */!function(e,t){}(window);",
}


def build(root: Path) -> Path:
    for rel, content in FILES.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return root


# ------------------------------------------------------------------ production-support fixtures
SUPPORT_FILES = {
    "src/main/java/com/acme/payment/PaymentException.java": """package com.acme.payment;

public class PaymentException extends RuntimeException {
    public PaymentException(String message, Throwable cause) { super(message, cause); }
}
""",
    "src/main/java/com/acme/payment/PaymentService.java": """package com.acme.payment;

import com.acme.model.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

@Service
public class PaymentService {
    private static final Logger log = LoggerFactory.getLogger(PaymentService.class);
    private static final String ERR_NO_USER = "payment.user.missing";

    private RestTemplate restTemplate = new RestTemplate();
    private int retryCount;

    @Value("${payment.gateway.url}")
    private String gatewayUrl;

    @Transactional
    public void charge(User user, long cents) {
        if (user == null) {
            throw new IllegalArgumentException(ERR_NO_USER);
        }
        try {
            String reply = restTemplate.postForObject(gatewayUrl + "/charge", cents, String.class);
            log.info("Charged user {} amount {}", user.getName(), cents);
        } catch (Exception e) {
            log.error("Gateway call failed for user " + user.getName());
            throw new PaymentException("Payment gateway unavailable", e);
        }
    }

    public void refund(User user) {
        try {
            restTemplate.postForObject(gatewayUrl + "/refund", user.getName(), String.class);
        } catch (Exception e) {
        }
        charge(user, 0);
    }
}
""",
    "src/main/java/com/acme/payment/PaymentController.java": """package com.acme.payment;

import com.acme.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/pay")
public class PaymentController {
    @Autowired
    private PaymentService paymentService;

    @PostMapping("/charge")
    public String charge(@RequestBody User user) {
        paymentService.charge(user, 100L);
        return "OK";
    }
}
""",
    "src/main/java/com/acme/payment/ErrorAdvice.java": """package com.acme.payment;

import org.springframework.web.bind.annotation.*;

@RestControllerAdvice
public class ErrorAdvice {
    @ExceptionHandler(PaymentException.class)
    public String onPayment(PaymentException e) {
        return "Payment failed, please try later";
    }
}
""",
    "src/main/java/com/acme/job/NightlyJob.java": """package com.acme.job;

import com.acme.payment.PaymentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class NightlyJob {
    @Autowired
    private PaymentService paymentService;

    @Scheduled(cron = "${job.nightly.cron}")
    public void run() {
        paymentService.refund(null);
    }
}
""",
    "src/main/resources/messages.properties": "payment.user.missing=User is required for payment\n",
    "src/main/resources/payment-dev.properties": "payment.gateway.url=http://localhost:9000\njob.nightly.cron=0 0 2 * * *\nhttp.timeout=5000\n",
    "src/main/resources/payment-prod.properties": "payment.gateway.url=https://pay.example.com\njob.nightly.cron=0 0 3 * * *\nhttp.timeout=30000\npayment.api.secret=abc123\n",
}


def build_support(root: Path) -> Path:
    build(root)
    for rel, content in SUPPORT_FILES.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return root


def line_of(source: str, needle: str) -> int:
    for i, line in enumerate(source.splitlines(), 1):
        if needle in line:
            return i
    raise KeyError(needle)


def sample_trace() -> str:
    src = SUPPORT_FILES["src/main/java/com/acme/payment/PaymentService.java"]
    ln = line_of(src, "restTemplate.postForObject(gatewayUrl + \"/charge\"")
    thr = line_of(src, "throw new PaymentException")
    ctl = line_of(SUPPORT_FILES["src/main/java/com/acme/payment/PaymentController.java"], "paymentService.charge(user, 100L)")
    return f"""2026-10-06 10:15:01,123 ERROR [http-nio-8080-exec-3] c.a.p.PaymentService - Gateway call failed for user Anna
com.acme.payment.PaymentException: Payment gateway unavailable
\tat com.acme.payment.PaymentService.charge(PaymentService.java:{thr})
\tat com.acme.payment.PaymentService$$EnhancerBySpringCGLIB$$1a2b.charge(<generated>)
\tat com.acme.payment.PaymentController.charge(PaymentController.java:{ctl})
\tat java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
\tat org.springframework.web.servlet.FrameworkServlet.service(FrameworkServlet.java:883)
Caused by: org.springframework.web.client.ResourceAccessException: I/O error on POST request: Read timed out
\tat org.springframework.web.client.RestTemplate.doExecute(RestTemplate.java:785)
\tat com.acme.payment.PaymentService.charge(PaymentService.java:{ln})
\t... 40 more
Caused by: java.net.SocketTimeoutException: Read timed out
\tat java.base/java.net.SocketInputStream.socketRead0(Native Method)
\t... 55 more
"""
