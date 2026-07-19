package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.Appointment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AppointmentRepository extends JpaRepository<Appointment, Long> {

    /** Lấy tất cả lịch khám của user, sắp xếp mới nhất trước */
    @Query("""
            SELECT a FROM Appointment a
            JOIN FETCH a.doctor d
            JOIN FETCH a.department dep
            WHERE a.user.id = :userId
            ORDER BY a.appointmentTime DESC NULLS LAST, a.createdAt DESC
            """)
    List<Appointment> findByUserIdWithDetails(@Param("userId") Long userId);

    /** Tìm lịch khám cụ thể, đảm bảo thuộc về user đó (bảo mật) */
    Optional<Appointment> findByIdAndUserId(Long id, Long userId);
}
