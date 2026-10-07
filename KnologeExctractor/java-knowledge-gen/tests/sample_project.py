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
