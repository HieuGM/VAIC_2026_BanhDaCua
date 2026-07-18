package com.hanoiheart.dataapi.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.OffsetDateTime;

/**
 * Appointment — lịch khám nghiệp vụ của Website.
 * Không lưu trong FHIR trong giai đoạn Hackathon.
 * Backend tự lấy fhir_patient_id từ user_patient_links sau khi xác thực.
 */
@Entity
@Table(name = "appointments", schema = "hospital")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Appointment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    /** Chỉ backend biết giá trị này — lấy từ user_patient_links */
    @Column(name = "fhir_patient_id")
    private String fhirPatientId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "doctor_id")
    private Doctor doctor;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "slot_id")
    private AppointmentSlot slot;

    @Column(name = "appointment_time")
    private OffsetDateTime appointmentTime;

    private String reason;

    /** PENDING | CONFIRMED | CANCELLED | COMPLETED | NO_SHOW */
    @Column(nullable = false)
    @Builder.Default
    private String status = "PENDING";

    @Column(name = "booking_channel", nullable = false)
    @Builder.Default
    private String bookingChannel = "WEB";

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private OffsetDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt;
}
