package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmail(String email);

    Optional<User> findByPhone(String phone);

    boolean existsByEmail(String email);

    boolean existsByPhone(String phone);

    /** Tìm theo email hoặc phone (dùng cho login) */
    default Optional<User> findByEmailOrPhone(String identifier) {
        Optional<User> byEmail = findByEmail(identifier);
        return byEmail.isPresent() ? byEmail : findByPhone(identifier);
    }
}
